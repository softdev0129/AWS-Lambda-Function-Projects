import json
import re
import requests
from urllib.parse import urlparse, urljoin
from xml.etree import ElementTree as ET
import pg8000
import os
import traceback
import re
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
from jobqueue_tracker import start_job_event, complete_job_event, fail_job_event



# Database connection details
db_host = os.getenv('DB_HOST', 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com')
db_port = int(os.getenv('DB_PORT', 5432))  # Default PostgreSQL port
db_database = os.getenv('DB_DATABASE', 'scraper_db')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'GWtxSGM4swxxhN3fMHRH')


def extract_contact_details(event, context):
    urls_to_process = get_urls_to_process()
    
    social_domains = [
        'linkedin.com',
        'twitter.com',
        'instagram.com',
        'facebook.com',
        'youtube.com',
        'tiktok.com'
    ]
    
    # Regex to find URLs within quotation marks
    url_pattern = re.compile(r'"(https?://[^"]+)"')
    # Simplified regex to find emails directly in text
    email_pattern = re.compile(r'\b[\w.-]+@[\w.-]+\.\w{2,4}\b')
    # Regex to find phone numbers
    phone_pattern = re.compile(r'(\+?( |-|\.)?\d{1,2}( |-|\.)?)?(\(?\d{3}\)?|\d{3})( |-|\.)?(\d{3}( |-|\.)?\d{4})')

    for url_info in urls_to_process:
        url = url_info.get('website')
        result_id = url_info.get('id')
        print(f'Processing URL - {url}')

        if not url or not isinstance(url, str):
            log_error(result_id, "Invalid URL")
            continue

        max_pages = 10  # Default to 10 pages for sitemap
        sitemap_url = url.rstrip('/') + '/sitemap.xml'
        
        contact_details = {
            'result_id': result_id,
            'Urls': [],  # List of URLs to be processed
            'Domain': urlparse(url).netloc,
            'emails': [],
            'phones': [],
            'linkedins': [],
            'twitters': [],
            'instagrams': [],
            'facebooks': [],
            'youtubes': [],
            'tiktoks': []
        }
        
        try:
            # Try to fetch the sitemap
            sitemap_response = requests.get(sitemap_url)
            sitemap_response.raise_for_status()
            sitemap_soup = ET.fromstring(sitemap_response.content)
            
            all_urls = [loc.text for loc in sitemap_soup.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            contact_urls = [url for url in all_urls if 'contact' in url.lower()]
            urls = contact_urls[:max_pages]
            if len(urls) < max_pages:
                remaining_slots = max_pages - len(urls)
                other_urls = [url for url in all_urls if url not in contact_urls][:remaining_slots]
                urls.extend(other_urls)
            
            if not urls:
                raise requests.RequestException("No URLs found in sitemap")

        except (requests.RequestException, ET.ParseError) as e:
            # If there's an error fetching the sitemap, fall back to the main URL
            urls = [url]
            log_error(result_id, f"Error fetching sitemap: {e}. Fallback to main URL")

        # Store URLs in contact_details
        contact_details['Urls'] = urls

        # Extract data from each URL
        for page_url in urls:
            print(f'Processing page URL - {page_url}')
            try:
                response = requests.get(page_url)
                response.raise_for_status()
                text_content = response.text
                
                # Extract emails directly in text
                emails = email_pattern.findall(text_content)
                contact_details['emails'].extend(emails)
                
                # Extract phones and filter out invalid ones
                extracted_phones = phone_pattern.findall(text_content)
                valid_phones = [phone[0] for phone in extracted_phones if re.match(r'^\+?\d[\d\s\-\(\)]{8,}$', phone[0])]
                contact_details['phones'].extend(valid_phones)

                
                # Extract social media links within quotation marks
                for match in url_pattern.findall(text_content):
                    for domain in social_domains:
                        if domain in match:
                            social_key = next(key for key in contact_details.keys() if domain.split('.')[0] in key)
                            contact_details[social_key].append(match)
                            break

            except requests.RequestException as e:
                log_error(result_id, f"Error fetching page URL {page_url}: {e}")
                continue
        
        # Deduplicate lists
        for key in contact_details:
            if isinstance(contact_details[key], list):
                contact_details[key] = list(set(contact_details[key]))
        
        # Store results in database, ensure we map to correct key names
        store_in_database({
            'result_id': contact_details['result_id'],
            'Urls': contact_details['Urls'],
            'Domain': contact_details['Domain'],
            'emails': contact_details['emails'],
            'phones': contact_details['phones'],
            'linkedIns': contact_details['linkedins'],
            'twitters': contact_details['twitters'],
            'instagrams': contact_details['instagrams'],
            'facebooks': contact_details['facebooks'],
            'youtubes': contact_details['youtubes'],
            'tiktoks': contact_details['tiktoks']
        })
        mark_url_processed(result_id)
    
    return {
        'statusCode': 200,
        'body': json.dumps({"status": "success"})
    }

def get_urls_to_process():
    conn = pg8000.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_database
    )
    cursor = conn.cursor()
    
    # Retrieve URLs where is_contact_details_extracted is false
    cursor.execute('''
        SELECT id, website FROM public.results
        WHERE is_contact_details_extracted = false
        AND website IS NOT NULL
        LIMIT 10
    ''')
    
    urls = [{'id': row[0], 'website': row[1]} for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    # return [{'id': 3587, 'website': 'https://www.theshed-restaurant.com//#contact-us'}]
    return urls

def store_in_database(contact_details):
    conn = pg8000.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_database
    )
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_details (
            id SERIAL PRIMARY KEY,
            result_id INT,
            urls TEXT[],
            domain TEXT,
            emails TEXT[],
            phones TEXT[],
            linkedins TEXT[],
            twitters TEXT[],
            instagrams TEXT[],
            facebooks TEXT[],
            youtubes TEXT[],
            tiktoks TEXT[],
            FOREIGN KEY (result_id) REFERENCES public.results(id)
        )
    ''')

    # Insert contact details into the table
    cursor.execute('''
        INSERT INTO contact_details (result_id, urls, domain, emails, phones, linkedins, twitters, instagrams, facebooks, youtubes, tiktoks)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        contact_details['result_id'],
        contact_details['Urls'],
        contact_details['Domain'],
        contact_details['emails'],
        contact_details['phones'],
        contact_details['linkedIns'],
        contact_details['twitters'],
        contact_details['instagrams'],
        contact_details['facebooks'],
        contact_details['youtubes'],
        contact_details['tiktoks']
    ))

    conn.commit()
    cursor.close()
    conn.close()

def mark_url_processed(result_id):
    conn = pg8000.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_database
    )
    cursor = conn.cursor()
    
    # Update is_contact_details_extracted to true for the processed URL
    cursor.execute('''
        UPDATE public.results
        SET is_contact_details_extracted = true
        WHERE id = %s
    ''', (result_id,))
    
    conn.commit()
    cursor.close()
    conn.close()

def log_error(result_id, message):
    conn = pg8000.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_database
    )
    cursor = conn.cursor()
    
    # Create error_logs table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS error_logs (
            id SERIAL PRIMARY KEY,
            result_id INT,
            message TEXT,
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            FOREIGN KEY (result_id) REFERENCES public.results(id)
        )
    ''')

    # Insert error log into the database
    cursor.execute('''
        INSERT INTO error_logs (result_id, message)
        VALUES (%s, %s)
    ''', (result_id, message))
    
    conn.commit()
    cursor.close()
    conn.close()

# Define the lambda_handler function
def lambda_handler(event, context):
    try:
        job_id = start_job_event()
        result = extract_contact_details(event, context)
        complete_job_event(job_id)
        return result
    except Exception as e:
        fail_job_event(job_id)
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}",
            'stackTrace': traceback.format_exc()
        }

if __name__ == "__main__":
    # Example event and context for local testing
    event = {}
    context = {}
    result = lambda_handler(event, context)
    print(result)

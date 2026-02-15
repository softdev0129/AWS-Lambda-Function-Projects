import json
import requests

API_KEY = "8a201685c6a0405ef436a1a25c44154c6531e5252b099ffcdfe052694d28b948b8ef36f7c35d78d4fa2a6db9139e9d274fccf33afce47dcb38aab379a94656686263b0f4299953bdfbc5041eae8b19018a7e68ea28b9279a76b83c5e4587d711859027b34c37ce31ed954e2a5d12764fea761b5fd0f15f9f51ce243de71f8589"
BASE_URL = "https://marchcroft.com"

def get_blog_data(slug):
    url = f"{BASE_URL}/api/blogs?filters[slug]={slug}&populate=image&populate=blogContent"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and 'data' in data and len(data['data']) > 0:
            blog = data['data'][0]
            title = blog['attributes']['blogTitle']
            details = blog['attributes']['blogContent']  # Updated key to match API structure
            image = blog['attributes']['image']['data']['attributes']['url']
            blog_url = f"{BASE_URL}/work/casestudies/{slug}"

            return {
                "title": title,
                "image": image,
                "url": blog_url,
                "details": details
            }
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def lambda_handler(event, context):
    # Extract slug from pathParameters
    slug = event['pathParameters']['slug']
    
    # Get the blog data
    blog_data = get_blog_data(slug)
    
    if blog_data:
        # HTML response with immediate JavaScript redirection and SEO meta tags
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{blog_data['title']}</title>

            <!-- Meta Tags for SEO and Social Media Sharing -->
            <meta name="description" content="{blog_data['details']}">
            <meta property="og:title" content="{blog_data['title']}">
            <meta property="og:description" content="{blog_data['details']}">
            <meta property="og:image" content="{blog_data['image']}">
            <!-- <meta property="og:url" content="{blog_data['url']}"> -->

            <meta name="twitter:card" content="summary_large_image">
            <meta name="twitter:title" content="{blog_data['title']}">
            <meta name="twitter:description" content="{blog_data['details']}">  <!-- Updated description -->
            <meta name="twitter:image" content="{blog_data['image']}">
            <!-- <meta name="twitter:url" content="{blog_data['url']}"> -->
            <!-- <meta http-equiv="refresh" content="0;url={blog_data['url']}"> -->

            <!-- Favicon -->
            <link rel="icon" href="https://marchcroft.s3.us-east-2.amazonaws.com/Marchcroft-Favicon-Logo.png" type="image/svg+xml">

            <!-- Immediate redirection using JavaScript -->
            <script type="text/javascript">
                window.location.href = "{blog_data['url']}";
            </script>

            <!-- Meta refresh tag as a fallback -->
            <!-- <meta http-equiv="refresh" content="0; url={blog_data['url']}"> -->
        </head>
        <body>
        </body>
        </html>
        """
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html'
            },
            'body': html_content
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({"message": "Blog not found"})
        }

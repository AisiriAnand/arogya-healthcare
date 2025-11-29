import requests
import re

print('🔍 Analyzing Karnataka Health GIS Website...')

try:
    response = requests.get('https://kgis.ksrsac.in/healthgis/', timeout=15)
    if response.status_code == 200:
        html_content = response.text
        print('✅ Website accessed successfully')
        print('Content length:', len(html_content))
        
        # Look for API endpoints
        api_patterns = re.findall(r'href=[\'"]([^\'"]*api[^\'"]*)[\'"]', html_content)
        print(f'Found {len(api_patterns)} API references:')
        for pattern in api_patterns[:10]:
            print(f'  API: {pattern}')
        
        # Look for data endpoints  
        data_patterns = re.findall(r'href=[\'"]([^\'"]*data[^\'"]*)[\'"]', html_content)
        print(f'Found {len(data_patterns)} data references:')
        for pattern in data_patterns[:10]:
            print(f'  Data: {pattern}')
            
        # Look for JavaScript files
        js_patterns = re.findall(r'src=[\'"]([^\'"]*\.js[^\'"]*)[\'"]', html_content)
        print(f'Found {len(js_patterns)} JavaScript files:')
        for pattern in js_patterns[:5]:
            print(f'  JS: {pattern}')
            
        # Test common API endpoints
        base_url = 'https://kgis.ksrsac.in'
        test_endpoints = [
            '/healthgis/api/districts',
            '/healthgis/api/hospitals', 
            '/healthgis/api/health-facilities',
            '/api/hospitals',
            '/healthgis/data/hospitals.json'
        ]
        
        print('\n🧪 Testing Common Endpoints:')
        for endpoint in test_endpoints:
            url = base_url + endpoint
            try:
                resp = requests.get(url, timeout=5)
                print(f'  {endpoint}: {resp.status_code}')
                if resp.status_code == 200:
                    print(f'    ✅ SUCCESS - Content type: {resp.headers.get("content-type", "unknown")}')
            except:
                print(f'  {endpoint}: Failed')
                
    else:
        print(f'❌ Failed to access website: {response.status_code}')
        
except Exception as e:
    print(f'❌ Error: {e}')

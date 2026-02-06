import json
import os
import re
from zipfile import ZipFile

REPO_INFO = {
    "name": "Cielo Repo",
    "id": "vpm.cielo-h",
    "url": "https://cielo-h.github.io/vpmRepo/index.json",
    "author": "cielo-h"
}

DOWNLOAD_URL_BASE = "https://raw.githubusercontent.com/cielo-h/vpmRepo/master/{plugin_name}/{filename}"

def extract_version_from_filename(filename):
    """Extract version number from filename"""
    # Pattern: vpm.{repositoryname}.{pluginname}-{version}.zip
    match = re.search(r'-(\d+\.\d+\.\d+)\.zip$', filename)
    if match:
        return match.group(1)
    return None

def extract_package_info(zip_path):
    """Read package.json from zip file"""
    try:
        with ZipFile(zip_path, 'r') as z:
            # Find package.json
            package_json_path = None
            for name in z.namelist():
                if name.endswith('package.json') and '/' not in name.replace('package.json', ''):
                    package_json_path = name
                    break
            
            if package_json_path is None:
                print(f"Warning: package.json not found in {zip_path}")
                return None
            
            package_data = json.loads(z.read(package_json_path).decode('utf-8'))
            return package_data
    except Exception as e:
        print(f"Error reading {zip_path}: {e}")
        return None

def scan_packages():
    """Scan packages in the repository"""
    packages = {}
    
    # Scan directories directly under the repository root
    for item in os.listdir('.'):
        if not os.path.isdir(item) or item.startswith('.'):
            continue
        
        plugin_dir = item
        print(f"Scanning directory: {plugin_dir}")
        
        # Find zip files in the directory
        if not os.path.exists(plugin_dir):
            continue
            
        for filename in os.listdir(plugin_dir):
            if not filename.endswith('.zip'):
                continue
            
            # Check pattern: vpm.{repositoryname}.{pluginname}-{version}.zip
            if not filename.startswith('vpm.'):
                continue
            
            zip_path = os.path.join(plugin_dir, filename)
            version = extract_version_from_filename(filename)
            
            if version is None:
                print(f"Warning: Could not extract version from {filename}")
                continue
            
            # Read package.json
            package_info = extract_package_info(zip_path)
            if package_info is None:
                continue
            
            package_name = package_info.get('name')
            if not package_name:
                print(f"Warning: No package name found in {zip_path}")
                continue
            
            # Build package information
            if package_name not in packages:
                packages[package_name] = {
                    "versions": {}
                }
            
            # Generate URL
            download_url = DOWNLOAD_URL_BASE.format(
                plugin_name=package_info.get('displayName'),
                filename=filename
            )
            
            # Add version information (with fixed key order)
            version_info = {
                "name": package_info.get('name'),
                "displayName": package_info.get('displayName'),
                "version": version,
                "unity": package_info.get('unity'),
                "description": package_info.get('description'),
                "url": download_url
            }
            
            # Add vpmDependencies if exists
            if 'vpmDependencies' in package_info:
                version_info['vpmDependencies'] = package_info['vpmDependencies']
            
            # Add author if exists
            if 'author' in package_info:
                version_info['author'] = package_info['author']
            
            packages[package_name]["versions"][version] = version_info
            print(f"Added: {package_name} version {version}")
    
    return packages

def generate_index():
    """Generate index.json"""
    # Collect package information
    packages = scan_packages()
    
    # Create index.json structure
    index = {
        "name": REPO_INFO["name"],
        "id": REPO_INFO["id"],
        "url": REPO_INFO["url"],
        "author": REPO_INFO["author"],
        "packages": packages
    }
    
    return index

def write_index(index_data):
    """Write index.json to file"""
    with open('index.json', 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False, sort_keys=False)
    print("index.json has been generated successfully!")

def main():
    print("Starting VPM index generation...")
    index = generate_index()
    write_index(index)
    print(f"Found {len(index['packages'])} package(s)")

if __name__ == '__main__':
    main()
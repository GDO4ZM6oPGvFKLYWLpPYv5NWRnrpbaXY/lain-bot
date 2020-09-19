import os, shutil

# Change working directory to the the project root directory (this script's dir)
root_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(root_dir)

# Copy skeleton .env
print("Creating .env...")
if os.path.exists('.env'):
    print(" '.env' exists! Skipping.")
else:    
    shutil.copy(os.path.join('skel','.env'), '.')

print('Done!')
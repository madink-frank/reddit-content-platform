#!/bin/bash

# Asset optimization script for production builds
# This script optimizes images, compresses files, and prepares assets for CDN deployment

set -e

APP_DIR=${1:-"admin-dashboard"}
DIST_DIR="$APP_DIR/dist"

echo "🚀 Optimizing assets for $APP_DIR..."

# Check if dist directory exists
if [ ! -d "$DIST_DIR" ]; then
    echo "❌ Build directory $DIST_DIR not found. Please run build first."
    exit 1
fi

# Install optimization tools if not available
if ! command -v imagemin &> /dev/null; then
    echo "📦 Installing imagemin-cli..."
    npm install -g imagemin-cli imagemin-pngquant imagemin-mozjpeg imagemin-svgo
fi

if ! command -v brotli &> /dev/null; then
    echo "📦 Installing brotli..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install brotli
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y brotli
    fi
fi

# Optimize images
echo "🖼️  Optimizing images..."
find "$DIST_DIR" -name "*.png" -exec imagemin {} --plugin=pngquant --out-dir="$DIST_DIR" \;
find "$DIST_DIR" -name "*.jpg" -o -name "*.jpeg" -exec imagemin {} --plugin=mozjpeg --out-dir="$DIST_DIR" \;
find "$DIST_DIR" -name "*.svg" -exec imagemin {} --plugin=svgo --out-dir="$DIST_DIR" \;

# Create compressed versions of text files
echo "🗜️  Creating compressed versions..."

# Gzip compression
find "$DIST_DIR" -type f \( -name "*.js" -o -name "*.css" -o -name "*.html" -o -name "*.json" -o -name "*.xml" -o -name "*.txt" \) | while read -r file; do
    if [ ! -f "$file.gz" ] || [ "$file" -nt "$file.gz" ]; then
        gzip -k -9 "$file"
        echo "  ✅ Gzipped: $(basename "$file")"
    fi
done

# Brotli compression
find "$DIST_DIR" -type f \( -name "*.js" -o -name "*.css" -o -name "*.html" -o -name "*.json" -o -name "*.xml" -o -name "*.txt" \) | while read -r file; do
    if [ ! -f "$file.br" ] || [ "$file" -nt "$file.br" ]; then
        brotli -k -9 "$file"
        echo "  ✅ Brotli: $(basename "$file")"
    fi
done

# Generate file manifest with hashes
echo "📋 Generating file manifest..."
MANIFEST_FILE="$DIST_DIR/manifest.json"
echo "{" > "$MANIFEST_FILE"
echo '  "generated": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",' >> "$MANIFEST_FILE"
echo '  "files": {' >> "$MANIFEST_FILE"

first=true
find "$DIST_DIR" -type f \( -name "*.js" -o -name "*.css" -o -name "*.png" -o -name "*.jpg" -o -name "*.svg" -o -name "*.woff" -o -name "*.woff2" \) | while read -r file; do
    if [ "$first" = true ]; then
        first=false
    else
        echo "," >> "$MANIFEST_FILE"
    fi
    
    relative_path=${file#$DIST_DIR/}
    file_hash=$(sha256sum "$file" | cut -d' ' -f1)
    file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
    
    echo -n "    \"$relative_path\": {" >> "$MANIFEST_FILE"
    echo -n "\"hash\": \"$file_hash\", " >> "$MANIFEST_FILE"
    echo -n "\"size\": $file_size" >> "$MANIFEST_FILE"
    echo -n "}" >> "$MANIFEST_FILE"
done

echo "" >> "$MANIFEST_FILE"
echo "  }" >> "$MANIFEST_FILE"
echo "}" >> "$MANIFEST_FILE"

# Generate cache headers configuration
echo "⚙️  Generating cache headers configuration..."
cat > "$DIST_DIR/.htaccess" << 'EOF'
# Cache configuration for Apache
<IfModule mod_expires.c>
    ExpiresActive on
    
    # Images
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
    ExpiresByType image/webp "access plus 1 year"
    ExpiresByType image/avif "access plus 1 year"
    
    # Fonts
    ExpiresByType font/woff "access plus 1 year"
    ExpiresByType font/woff2 "access plus 1 year"
    ExpiresByType font/ttf "access plus 1 year"
    ExpiresByType font/eot "access plus 1 year"
    ExpiresByType font/otf "access plus 1 year"
    
    # CSS and JavaScript
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType text/javascript "access plus 1 year"
    
    # HTML
    ExpiresByType text/html "access plus 1 hour"
    
    # JSON
    ExpiresByType application/json "access plus 1 hour"
    
    # XML
    ExpiresByType application/xml "access plus 1 hour"
    ExpiresByType text/xml "access plus 1 hour"
</IfModule>

<IfModule mod_headers.c>
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    
    # Cache control
    <FilesMatch "\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$">
        Header set Cache-Control "public, max-age=31536000, immutable"
    </FilesMatch>
    
    <FilesMatch "\.(html|htm)$">
        Header set Cache-Control "public, max-age=3600, must-revalidate"
    </FilesMatch>
</IfModule>

<IfModule mod_deflate.c>
    # Compress text files
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
    AddOutputFilterByType DEFLATE application/json
</IfModule>
EOF

# Generate _headers file for Netlify
cat > "$DIST_DIR/_headers" << 'EOF'
# Cache headers for Netlify
/*
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin

/*.js
  Cache-Control: public, max-age=31536000, immutable

/*.css
  Cache-Control: public, max-age=31536000, immutable

/*.png
  Cache-Control: public, max-age=31536000, immutable

/*.jpg
  Cache-Control: public, max-age=31536000, immutable

/*.svg
  Cache-Control: public, max-age=31536000, immutable

/*.woff
  Cache-Control: public, max-age=31536000, immutable

/*.woff2
  Cache-Control: public, max-age=31536000, immutable

/*.html
  Cache-Control: public, max-age=3600, must-revalidate

/*.json
  Cache-Control: public, max-age=3600
EOF

# Generate vercel.json for Vercel
cat > "$DIST_DIR/vercel.json" << 'EOF'
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    },
    {
      "source": "/(.*\\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot))",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/(.*\\.(html|htm))",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600, must-revalidate"
        }
      ]
    }
  ]
}
EOF

# Calculate and display optimization results
echo ""
echo "📊 Optimization Results:"
echo "======================="

# Count files
total_files=$(find "$DIST_DIR" -type f | wc -l)
compressed_files=$(find "$DIST_DIR" -name "*.gz" | wc -l)
brotli_files=$(find "$DIST_DIR" -name "*.br" | wc -l)

echo "Total files: $total_files"
echo "Gzip compressed: $compressed_files"
echo "Brotli compressed: $brotli_files"

# Calculate total size
if [[ "$OSTYPE" == "darwin"* ]]; then
    total_size=$(find "$DIST_DIR" -type f ! -name "*.gz" ! -name "*.br" -exec stat -f%z {} + | awk '{sum+=$1} END {print sum}')
else
    total_size=$(find "$DIST_DIR" -type f ! -name "*.gz" ! -name "*.br" -exec stat -c%s {} + | awk '{sum+=$1} END {print sum}')
fi

echo "Total size: $(numfmt --to=iec $total_size)"

# Show largest files
echo ""
echo "📁 Largest files:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    find "$DIST_DIR" -type f ! -name "*.gz" ! -name "*.br" -exec stat -f"%z %N" {} + | sort -rn | head -10 | while read size file; do
        echo "  $(numfmt --to=iec $size) - $(basename "$file")"
    done
else
    find "$DIST_DIR" -type f ! -name "*.gz" ! -name "*.br" -exec stat -c"%s %n" {} + | sort -rn | head -10 | while read size file; do
        echo "  $(numfmt --to=iec $size) - $(basename "$file")"
    done
fi

echo ""
echo "✅ Asset optimization complete!"
echo "📁 Optimized files are in: $DIST_DIR"
echo "📋 File manifest: $DIST_DIR/manifest.json"
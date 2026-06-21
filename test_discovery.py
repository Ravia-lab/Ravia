from ravia_ki.discovery.web_discovery import WebDiscovery

disc = WebDiscovery()

manufacturer = "Vaillant"
model = "Standard"

result = disc.discover_device(manufacturer, model)

print("Produktseiten:", result.product_pages)
print("PDFs:", result.datasheets)
print("Bilder:", result.images)
print("ZIP:", result.zip_files)

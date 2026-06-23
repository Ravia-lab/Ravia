from ravia_ki.pipeline.pipeline import Pipeline

urls = [
    "https://www.lg.com/de/business/download/airsolution/R32_Monobloc_Silent%20Monobloc_Leaflet_DE_20210208%5B20210208_235539521%5D.pdf"
]

pipeline = Pipeline()
pipeline.process_urls(urls)

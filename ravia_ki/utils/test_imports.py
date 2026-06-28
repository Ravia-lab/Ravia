print("🔍 Starte Import-Test...")

try:
    import ravia_ki
    print("✅ Paket 'ravia_ki' gefunden!")
except Exception as e:
    print("❌ Fehler beim Import von 'ravia_ki':", e)

try:
    from ravia_ki.discovery.discovery_pipeline import DiscoveryPipeline
    print("✅ DiscoveryPipeline importiert!")
except Exception as e:
    print("❌ Fehler beim Import von DiscoveryPipeline:", e)

try:
    from ravia_ki.engine.Heizlast import Heizlast
    print("✅ Heizlast-Engine importiert!")
except Exception as e:
    print("❌ Fehler beim Import der Heizlast-Engine:", e)

try:
    from ravia_ki.ui.dashboard import Dashboard
    print("✅ Dashboard importiert!")
except Exception as e:
    print("❌ Fehler beim Import des Dashboards:", e)

print("🔚 Test abgeschlossen.")

import pkgutil
import ravia_ki

print("🔍 Prüfe Paketstruktur…")

print("\n📁 Verfügbare Submodule in ravia_ki:")
for module in pkgutil.iter_modules(ravia_ki.__path__):
    print(" -", module.name)

print("\n🔍 Prüfe discovery-Verzeichnis:")
import ravia_ki.discovery
for module in pkgutil.iter_modules(ravia_ki.discovery.__path__):
    print(" -", module.name)

print("\n🔍 Prüfe engine-Verzeichnis:")
import ravia_ki.engine
for module in pkgutil.iter_modules(ravia_ki.engine.__path__):
    print(" -", module.name)

print("\n🔍 Prüfe ui-Verzeichnis:")
import ravia_ki.ui
for module in pkgutil.iter_modules(ravia_ki.ui.__path__):
    print(" -", module.name)

print("\n🔚 Strukturtest abgeschlossen.")

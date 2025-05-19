try:
    import moomoo_api
    print("moomoo_api module imported successfully")
    print(f"moomoo_api version: {moomoo_api.__version__}")
    print(f"moomoo_api dir: {dir(moomoo_api)}")
except ImportError as e:
    print(f"Failed to import moomoo_api: {e}")

try:
    from moomoo_api import OpenQuoteContext
    print("OpenQuoteContext imported successfully")
except ImportError as e:
    print(f"Failed to import OpenQuoteContext: {e}")

try:
    from futu import OpenQuoteContext
    print("futu.OpenQuoteContext imported successfully")
except ImportError as e:
    print(f"Failed to import futu.OpenQuoteContext: {e}")

try:
    import futu
    print("futu module imported successfully")
    print(f"futu version: {futu.__version__}")
    print(f"futu dir: {dir(futu)}")
except ImportError as e:
    print(f"Failed to import futu: {e}")

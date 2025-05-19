try:
    import moomoo
    print("moomoo module imported successfully")
    print(f"moomoo version: {moomoo.__version__}")
except ImportError as e:
    print(f"Failed to import moomoo: {e}")

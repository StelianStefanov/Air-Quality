import time

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559

    ltr559 = LTR559()
except ImportError:
    import ltr559


if __name__ == "__main__":
    while True:
        print(ltr559.get_lux())
        time.sleep(1)

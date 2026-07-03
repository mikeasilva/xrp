def noise_filter(val, threshold, default_return=0.0):
    if abs(val) < threshold:
        return default_return
    return val

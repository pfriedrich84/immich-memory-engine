from memory_engine.geoutil import haversine_m


def test_haversine_zero():
    assert haversine_m(48.0, 16.0, 48.0, 16.0) == 0

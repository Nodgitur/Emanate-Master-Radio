import unittest
from rfm69_bonnet import pressure_to_altitude
from rfm69_bonnet import weather_api_data

# Creating a class with a case of unit tests
class TestRfm69Bonnet(unittest.TestCase):
    
    def test_pressure_to_altitude(self):
        
        # Given
        local_pressure = "1028"
        sea_level_pressure = "1032"
        expected_altitude = "33.0"
        
        # When
        result = pressure_to_altitude(local_pressure, sea_level_pressure)
        
        # Then
        self.assertEqual(result, expected_altitude)
    
    def test_weather_api_data(self):
        
        # Given
        locale = "Ontario,CA"
        open_weather_map_api_key = "adsa883n1ks2dk"
        isTest = True
        expected_sea_level_pressure = '1020'
        
        # When
        result = weather_api_data(locale, open_weather_map_api_key, isTest)
        
        # Then
        self.assertEqual(result, expected_sea_level_pressure)
        
    # token_refresh, and run functions are not testable due to exposing sensitive data
    
if __name__ == '__main__':
    unittest.main()
    

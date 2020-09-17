# Usage

## import
```python
import utm

```

## (latitude, longitude) -> (easting, northing, zone_number, zone_letter)
```python
utm.latlng_to_utm(39.90708, 116.39122)
>>> (447964.1787141931, 4417621.446654665, 50, 'S')
```

## (easting, northing, zone_number, zone_letter) -> (latitude, longitude)
```python
utm.utm_to_latlng(447964.1787141931, 4417621.446654665, 50, zone_letter='S')
>>> (39.90708000039096, 116.39121999999648)
```

The following is valid too.
```python
utm.utm_to_latlng(447964.1787141931, 4417621.446654665, 50, is_northern=True)
utm.utm_to_latlng(447964.1787141931, 4417621.446654665, 50, zone_letter='S', is_northern=True)
```

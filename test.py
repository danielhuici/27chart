from pytube import Playlist, YouTube


pl = Playlist('https://www.youtube.com/playlist?list=PLaJq2Gw03Eigv6RQqXKmUP8lPO3IoXbEl')
print(pl.initial_data)

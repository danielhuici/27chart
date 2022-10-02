from pytube import Playlist, YouTube


p = Playlist('https://www.youtube.com/playlist?list=PLaJq2Gw03EigZ484uySxuX1O_0aPBg4Yx')
print(str(len(list(p.videos))))

#yt = YouTube('https://www.youtube.com/watch?v=DrcsC05YgFw')
#print(yt.description)
from tube_dl import Playlist, Youtube
pl = Playlist('https://music.youtube.com/playlist?list=PLTy__vzNAW6C6sqmp6ddhsuaLsodKDEt_').videos
for i in pl:
    yt = Youtube(f'https://youtube.com/watch?v={i}')
    #yt.formats.first().download()
import moviepy, os, importlib
print('moviepy', moviepy.__version__)
pkgdir = os.path.dirname(moviepy.__file__)
print('pkgdir', pkgdir)
print('has editor file', os.path.exists(os.path.join(pkgdir, 'editor.py')))
print('list', os.listdir(pkgdir))
mod = importlib.import_module('moviepy.video.io.VideoFileClip')
print('VideoFileClip module loaded', mod)
print('VideoFileClip attr exists', hasattr(mod, 'VideoFileClip'))

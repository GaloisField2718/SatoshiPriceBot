import qrcode
<<<<<<< HEAD
import sys

data = sys.argv[1]
qr = qrcode.QRCode(border=4, box_size=10)
qr.add_data(data)

qr.make(fit=True)
img = qr.make_image(fill_color="white", back_color="black")
img.save(f'data.png')

=======

qr = qrcode.QRCode(border=4, box_size=10)
qr.add_data('bc1qxxuuxmlp3wxuyn6uuqw448nzaafuqdxc076m9k')
qr.make(fit=True)
img = qr.make_image(fill_color="white", back_color="black")
img.save('qr_myaddress.png')
>>>>>>> refs/remotes/origin/main

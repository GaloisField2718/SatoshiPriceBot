import qrcode

qr = qrcode.QRCode(border=4, box_size=10)
qr.add_data('bc1qxxuuxmlp3wxuyn6uuqw448nzaafuqdxc076m9k')
qr.make(fit=True)
img = qr.make_image(fill_color="white", back_color="black")
img.save('qr_myaddress.png')

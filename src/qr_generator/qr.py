import qrcode

qr = qrcode.QRCode(border=4, box_size=10)
qr.add_data('bc1phpx4kqdqnkgf2ujugchk9vc5uphs2ngx46l8tfynly8f5zcvfccst42g7k')
qr.make(fit=True)
img = qr.make_image(fill_color="white", back_color="black")
img.save('qr_myaddress.png')

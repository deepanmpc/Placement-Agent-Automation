from reportlab.pdfgen import canvas
c = canvas.Canvas("dummy.pdf")
c.drawString(100, 750, "SKILLS\nReact, Next.js, Django")
c.save()

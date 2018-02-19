import web

render = web.template.render('templates/')
urls = (
    '/add/(.*)/(.*)','index'
)

class index:
    def GET(self,a,b):
		print a,b
		#c = int(a) + int(b)
		return render.index(a,b)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

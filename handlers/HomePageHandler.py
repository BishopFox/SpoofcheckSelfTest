from handlers.BaseHandlers import BaseHandler


class HomePageHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render('home.html')

# from Backend.Router import router
# from Backend import app
#
#cd
# app.register_blueprint(router)
#
# if __name__ == '__main__':
#     app.run(debug=True)
#



from Backend.Router import router
from Backend import app

app.register_blueprint(router)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)




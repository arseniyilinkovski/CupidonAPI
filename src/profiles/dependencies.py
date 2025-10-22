from nsfw_detector import predict


def get_nsfw_model(app) -> "Model":
    return app.state.nsfw_model



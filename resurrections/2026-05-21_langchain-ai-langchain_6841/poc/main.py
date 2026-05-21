import sys
import importlib.util

class PydanticV2Model:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def get_config(cls):
        return {"use_pydantic_v2": True}

class LangChainModel:
    def __init__(self, model_class):
        self.model_class = model_class

    def __getattr__(self, name):
        try:
            return getattr(self.model_class, name)
        except AttributeError:
            raise AttributeError(f"{self.model_class.__name__} object has no attribute {name}")

def get_pydantic_version():
    try:
        import pydantic
        return pydantic.__version__
    except ImportError:
        return None

def use_pydantic_v2():
    pydantic_version = get_pydantic_version()
    if pydantic_version and pydantic_version >= "2.0.0":
        return True
    return False

def create_model_class(use_v2):
    if use_v2:
        return PydanticV2Model
    else:
        return object

def main():
    try:
        use_v2 = use_pydantic_v2()
        model_class = create_model_class(use_v2)
        LangChainModel(model_class)
        print("Pydantic version used: " + ("v2" if use_v2 else "v1"))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
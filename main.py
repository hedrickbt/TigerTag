from tigertag.engine import EnvironmentEngineManagerBuilder
from tigertag.engine import EngineManager
from tigertag.engine import EngineListener

# ENGINE_IMAGGA_NAME=tigertag.engine.imagga.ImaggaEngine
# ENGINE_IMAGGA_ENABLED=True
# ENGINE_IMAGGA_API_KEY=<VALUE>
# ENGINE_IMAGGA_API_SECRET=<VALUE>
# ENGINE_IMAGGA_API_URL=https://api.imagga.com/v2
# DB_URL=sqlite:///tigertag.db

FOUND_TAGS = {}


def on_tags(engine, tag_info):
    print(engine.name)
    FOUND_TAGS[tag_info['file_path']] = tag_info

if __name__ == "__main__":
    el = EngineListener()
    el.on_tags = on_tags
    emb = EnvironmentEngineManagerBuilder(EngineManager)
    em = emb.build()
    em.listeners.append(el)
    em.run()
    print(FOUND_TAGS)

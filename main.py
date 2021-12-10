from tigertag.engine import EnvironmentEngineManagerBuilder
from tigertag.engine import EngineManager

# ENGINE_IMAGGA_NAME=tigertag.engine.imagga.ImaggaEngine
# ENGINE_IMAGGA_ENABLED=True
# ENGINE_IMAGGA_API_KEY=<VALUE>
# ENGINE_IMAGGA_API_SECRET=<VALUE>
# ENGINE_IMAGGA_API_URL=https://api.imagga.com/v2
# ENGINE_IMAGGA_INPUT_LOCATION=data/images/input
# ENGINE_IMAGGA_OUTPUT_LOCATION=data/images/output
# DB_URL=sqlite:///tigertag.db

FOUND_TAGS = {}


def on_tags(engine, tag_info):
    print(engine.name)
    FOUND_TAGS[tag_info['file_path']] = tag_info

if __name__ == "__main__":
    emb = EnvironmentEngineManagerBuilder(EngineManager)
    em = emb.build()
    em.on_tags = on_tags
    em.run()
    print(FOUND_TAGS)

from agents import ADPostPatch, HumanUser, AdBot
from model import RedNoteADEcoModel
from mesa.experimental.devs import ABMSimulator
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)

def rednote_portrayal(agent):
    if agent is None:
        return

    portrayal = {
        "size": 40,
    }

    if isinstance(agent, HumanUser):
        portrayal["color"] = "tab:yellow"
        portrayal["marker"] = "o"
        portrayal["zorder"] = 2
    elif isinstance(agent, AdBot):
        portrayal["color"] = "tab:green"
        portrayal["marker"] = "^"
        portrayal["zorder"] = 2
    elif isinstance(agent, ADPostPatch):
        if agent.fully_grown:
            portrayal["color"] = "tab:blue"
        else:
            portrayal["color"] = "tab:red"
        portrayal["marker"] = "s"
        portrayal["size"] = 75

    return portrayal
    # if isinstance(agent, OriginalPost):
    #     return {"Shape": "star", "Color": "red", "r": 8}
    # elif isinstance(agent, AdPost):
    #     return {
    #         "Shape": "rect",
    #         "Color": "blue",
    #         "Filled": True,
    #         "Layer": 2,
    #         "w": agent.influence_radius*2,
    #         "h": agent.influence_radius*2
    #     }
    # elif isinstance(agent, AdBot):
    #     return {"Shape": "triangle", "Color": "green", "r": 6}
    # elif isinstance(agent, HumanUser):
    #     return {"Shape": "circle", "Color": "yellow", "r": 4}


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "ad_post": {
        "type": "Select",
        "value": True,
        "values": [True, False],
        "label": "Platform AI detection disabled?",
    },
    "adpost_regrowth_time": Slider("Grass Regrowth Time", 20, 1, 50),
    "initial_adbot": Slider("Initial Number of ADBots", 100, 10, 300),
    "adbot_rep": Slider("Sheep Reproduction Rate", 0.04, 0.01, 1.0, 0.01),
    "initial_user": Slider("Initial Human Users", 10, 5, 100),
    "user_rep": Slider(
        "Human Report Torlerance",
        0.05,
        0.01,
        1.0,
        0.01,
    ),
    "user_pay_from_ad=": Slider("User Payment Rate from AD", 20, 1, 50),
    "adbot_gain_from_adpost": Slider("ADBot Evasion strategy", 4, 1, 10),
}

# # 新增控制参数
# model_params = {
#     "report_threshold": Slider("举报阈值", 5, 1, 20),
#     "detection_interval": Slider("检测间隔", 100, 50, 200),
#     "initial_bots": Slider("初始机器人数量", 20, 5, 50),
#     "initial_humans": Slider("初始用户数量", 50, 10, 100)
# }


def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))

space_component = make_space_component(
    rednote_portrayal, draw_grid=False, post_process=post_process_space
)
lineplot_component = make_plot_component(
    {"Purchases driven by AD": "tab:orange", "Number of Undetected Bots": "tab:cyan", "Number of ADPost": "tab:green"},
    post_process=post_process_lines,
)
# # 新增统计组件
# lineplot_component = make_plot_component({
#     "Active_Bots": "tab:green",
#     "Purchases": "tab:orange",
#     "Detection_Rate": "tab:red",
#     "Ad_Influence": "tab:purple"
# })


simulator = ABMSimulator()
model = RedNoteADEcoModel()

page = SolaraViz(
    model,
    components=[space_component, lineplot_component],
    model_params=model_params,
    name="redNote ADBot Eco Simulation",
    simulator=simulator,
)
page  # noqa

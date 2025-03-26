import math

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.experimental.cell_space  import OrthogonalVonNeumannGrid
from agents import AdBot, HumanUser, ADPostPatch
from mesa.experimental.devs import ABMSimulator

class RedNoteADEcoModel(Model):

    description = (
        "A model for simulating ADPost and Platform AI detection on rednote ecosystem modelling."
    )

    def __init__(
        self,
        width=40,
        height=40,
        initial_adbot=30,
        initial_user=50,
        adbot_rep=0.04,
        user_rep=0.05,
        user_pay_from_ad=20,
        ad_post=True,
        adpost_regrowth_time=30,
        adbot_gain_from_adpost=4,
        seed=None,
        simulator: ABMSimulator = None,
    ):
        super().__init__(seed=seed)
        self.simulator = simulator
        self.simulator.setup(self)

        # Initialize model parameters
        self.height = height
        self.width = width
        self.ad_post = ad_post

        # Create grid using experimental cell space
        self.grid = OrthogonalVonNeumannGrid(
            [self.height, self.width],
            torus=True,
            capacity=math.inf,
            random=self.random,
        )

        # Set up data collection
        model_reporters = {
            "Human User": lambda m: len(m.agents_by_type[HumanUser]),
            "ADBots": lambda m: len(m.agents_by_type[AdBot]),
        }
        if ad_post:
            model_reporters["AD Posts"] = lambda m: len(
                m.agents_by_type[ADPostPatch].select(lambda a: a.fully_grown)
            )

        self.datacollector = DataCollector(model_reporters)


        # # Create Origin Post:
        # for i in range(inital_op):
        #     OriginalPost(self, self.grid.select_random_empty_cell())

        # Create ADBOTs:
        AdBot.create_agents(
            self,
            initial_adbot,
            energy=self.rng.random((initial_adbot,)) * 2 * adbot_gain_from_adpost,
            p_reproduce=adbot_rep,
            energy_from_food=adbot_gain_from_adpost,
            cell=self.random.choices(self.grid.all_cells.cells, k=initial_adbot),
        )

        # Create Human Users:
        HumanUser.create_agents(
            self,
            initial_user,
            energy=self.rng.random((initial_user,)) * 2 * user_pay_from_ad,
            p_reproduce=user_rep,
            energy_from_food=user_pay_from_ad,
            cell=self.random.choices(self.grid.all_cells.cells, k=initial_user),
        )

        # ADBots Create ADPost arround Origin Post:
        if ad_post:
            possibly_fully_grown = [True, False]
            for cell in self.grid:
                fully_grown = self.random.choice(possibly_fully_grown)
                countdown = (
                    0 if fully_grown else self.random.randrange(0, adpost_regrowth_time)
                )
                ADPostPatch(self, countdown, adpost_regrowth_time, cell)

        # Collect initial data
        self.running = True
        self.datacollector.collect(self)


    def step(self):
        """Execute one step of the model."""
        # First activate all sheep, then all wolves, both in random order
        self.agents_by_type[AdBot].shuffle_do("step")
        self.agents_by_type[HumanUser].shuffle_do("step")

        # Collect data
        self.datacollector.collect(self)



    # def step(self):
    #     super().step()
    #     # 平台检测机制
    #     if self.schedule.steps % self.detection_interval == 0:
    #         self.detect_suspicious_actors()
    #     # 动态调整广告影响范围
    #     for ad in self.ads:
    #         ad.influence_radius = 1 + ad.likes // 10
    #         if ad.reports > self.report_threshold:
    #             ad.is_blocked = True
    #             ad.influence_radius = max(1, ad.influence_radius//2)
    #
    # def detect_suspicious_actors(self):
    #     for bot in self.ad_bots:
    #         if bot.reports > 3 * self.report_threshold:
    #             bot.remove()
    #             self.detection_count += 1
    #     for ad in self.ads:
    #         if ad.reports > 5 * self.report_threshold:
    #             ad.remove()

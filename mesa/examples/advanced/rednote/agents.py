from mesa.experimental.cell_space  import CellAgent, FixedAgent

# class OriginalPost(FixedAgent):
#     """原始文章（红色五角星）"""
#     def __init__(self, model, cell):
#         super().__init__(model)
#         self.cell = cell
#         self.influence_radius = 3  # 初始影响范围

class AdPost(FixedAgent):
    """广告贴（蓝色网格）"""
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
        self.likes = 0
        self.reports = 0
        self.influence_radius = 1
        self.is_blocked = False

class ADPostPatch(FixedAgent):
    """A patch of ADPost posted by ADBot and can be reported by HumanUser, then be detected by PlatformAI."""

    @property
    def fully_grown(self):
        """Whether the AD Post is fully grown."""
        return self._fully_grown

    @fully_grown.setter
    def fully_grown(self, value: bool) -> None:
        """Set grass growth state and schedule regrowth if eaten."""
        self._fully_grown = value

        if not value:  # If grass was just eaten
            self.model.simulator.schedule_event_relative(
                setattr,
                self.grass_regrowth_time,
                function_args=[self, "fully_grown", True],
            )

    def __init__(self, model, countdown, grass_regrowth_time, cell):
        """Create a new patch of ADPost.

        Args:
            model: Model instance
            countdown: Time until grass is fully grown again
            grass_regrowth_time: Time needed to regrow after being eaten
            cell: Cell to which this grass patch belongs
        """
        super().__init__(model)
        self._fully_grown = countdown == 0
        self.grass_regrowth_time = grass_regrowth_time
        self.cell = cell

        # Schedule initial growth if not fully grown
        if not self.fully_grown:
            self.model.simulator.schedule_event_relative(
                setattr, countdown, function_args=[self, "fully_grown", True]
            )


class Users(CellAgent):
    """The base user(Human and ADBot) class."""

    def __init__(
        self, model, energy=8, p_reproduce=0.04, energy_from_food=4, cell=None
    ):
        """Initialize an animal.

        Args:
            model: Model instance
            energy: Starting amount of energy
            p_reproduce: Probability of reproduction (asexual)
            energy_from_food: Energy obtained from 1 unit of food
            cell: Cell in which the animal starts
        """
        super().__init__(model)
        self.energy = energy
        self.p_reproduce = p_reproduce
        self.energy_from_food = energy_from_food
        self.cell = cell

    def spawn_offspring(self):
        """Create offspring by splitting energy and creating new instance."""
        self.energy /= 2
        self.__class__(
            self.model,
            self.energy,
            self.p_reproduce,
            self.energy_from_food,
            self.cell,
        )

    def feed(self):
        """Abstract method to be implemented by subclasses."""

    def step(self):
        """Execute one step of the animal's behavior."""
        # Move to random neighboring cell
        self.move()

        self.energy -= 1

        # Try to feed
        self.feed()

        # Handle death and reproduction
        if self.energy < 0:
            self.remove()
        elif self.random.random() < self.p_reproduce:
            self.spawn_offspring()

class AdBot(Users):
    """ADBot that walks around and post ADPost."""
    """广告机器人（绿色三角）"""

    def feed(self):
        """If possible, eat grass at current location."""
        ad_post_patch = next(
            obj for obj in self.cell.agents if isinstance(obj, ADPostPatch)
        )
        if ad_post_patch.fully_grown:
            self.energy += self.energy_from_food
            ad_post_patch.fully_grown = False

    def move(self):
        """Move towards a cell where there isn't a human, and preferably with grown ADPost."""
        cells_without_wolves = self.cell.neighborhood.select(
            lambda cell: not any(isinstance(obj, HumanUser) for obj in cell.agents)
        )
        # If all surrounding cells have wolves, stay put
        if len(cells_without_wolves) == 0:
            return

        # Among safe cells, prefer those with grown grass
        cells_with_grass = cells_without_wolves.select(
            lambda cell: any(
                isinstance(obj, ADPostPatch) and obj.fully_grown for obj in cell.agents
            )
        )
        # Move to a cell with grass if available, otherwise move to any safe cell
        target_cells = (
            cells_with_grass if len(cells_with_grass) > 0 else cells_without_wolves
        )
        self.cell = target_cells.select_random_cell()

    # def __init__(self, model, energy=20,  **kwargs):
    #     super().__init__(model,  **kwargs)
    #     self.energy = energy
    #     self.target_posts = []  # 目标原始文章列表
    #     self.report_risk = 0
    #
    # def step(self):
    #     self.find_target_posts()
    #     self.publish_ads()
    #     self.collaborative_likes()
    #     self.avoid_detection()
    #     self.energy -= 1
    #     if self.energy < 0:
    #         self.remove()
    #
    # def find_target_posts(self):
    #     # 寻找周围3格内的原始文章
    #     nearby_cells = self.cell.get_neighbors(3)
    #     self.target_posts = [cell for cell in nearby_cells if isinstance(cell.agent, OriginalPost)]
    #
    # def publish_ads(self):
    #     if self.random.random() < self.publish_prob:
    #         # 在目标文章周围随机位置发布广告
    #         target_cell = self.random.choice(self.target_posts).get_random_adjacent_cell()
    #         AdPost(self.model, target_cell)
    #
    # def collaborative_likes(self):
    #     # 协作点赞最近的广告贴
    #     nearby_ads = self.find_nearby_ads()
    #     if nearby_ads:
    #         selected_ad = self.random.choice(nearby_ads)
    #         selected_ad.likes += 1
    #         self.model.update_ad_influence(selected_ad)
    #
    # def avoid_detection(self):
    #     # 根据举报风险调整行为
    #     if self.report_risk > 0.7:
    #         self.publish_prob *= 0.5  # 降低发布频率

class HumanUser(CellAgent):
    """Human users that walks around, pay by the ADPost and then report ADPost."""
    """人类用户（黄色圆点）"""

    def feed(self):
        """If possible, eat a sheep at current location."""
        sheep = [obj for obj in self.cell.agents if isinstance(obj, AdBot)]
        if sheep:  # If there are any sheep present
            sheep_to_eat = self.random.choice(sheep)
            self.energy += self.energy_from_food
            sheep_to_eat.remove()

    def move(self):
        """Move to a neighboring cell, preferably one with sheep."""
        cells_with_sheep = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, AdBot) for obj in cell.agents)
        )
        target_cells = (
            cells_with_sheep if len(cells_with_sheep) > 0 else self.cell.neighborhood
        )
        self.cell = target_cells.select_random_cell()

    # def __init__(self, model,  **kwargs):
    #     super().__init__(model,  **kwargs)
    #     self.has_reported = False
    #
    # def step(self):
    #     self.random_move()
    #     self.interact_with_ads()
    #     self.check_ad_reports()
    #
    # def interact_with_ads(self):
    #     current_cell = self.cell
    #     ads_in_cell = [a for a in current_cell.agents if isinstance(a, AdPost)]
    #     if ads_in_cell:
    #         ad = self.random.choice(ads_in_cell)
    #         action = self.random.choices(['like', 'buy', 'report'],
    #                                     weights=[0.6, 0.3, 0.1])[0]
    #         if action == 'like':
    #             ad.likes += 1
    #         elif action == 'buy':
    #             self.model.purchase_count += 1
    #         elif action == 'report':
    #             ad.reports += 1
    #             self.has_reported = True
    #
    # def check_ad_reports(self):
    #     # 用户举报后可能触发连锁举报
    #     if self.has_reported and self.random.random() < 0.3:
    #         nearby_ads = self.find_nearby_ads()
    #         for ad in nearby_ads:
    #             ad.reports += 1

import torch
from easydict import EasyDict

from core.envs import SimpleCarlaEnv
from core.utils.others.tcp_helper import parse_carla_tcp
from core.eval import SingleCarlaEvaluator
from ding.policy import PPOPolicy
from ding.utils import set_pkg_seed
from ding.utils.default_helper import deep_merge_dicts
from demo.simple_rl.model import PPORLModel
from demo.simple_rl.env_wrapper import DiscreteBenchmarkEnvWrapper

eval_config = dict(
    env=dict(
        simulator=dict(
            town='Town01',
            disable_two_wheels=True,
            verbose=False,
            waypoint_num=32,
            planner=dict(
                type='behavior',
                resolution=1,
            ),
            obs=(
                dict(
                    name='birdview',
                    type='bev',
                    size=[32, 32],
                    pixels_per_meter=1,
                    pixels_ahead_vehicle=14,
                ),
            )
        ),
        col_is_failure=True,
        stuck_is_failure=True,
        ignore_light=True,
        visualize=dict(type='birdview', outputs=['show']),
    ),
    model=dict(action_shape=21,),
    policy=dict(
        cuda=True,
        ckpt_path='',
    ),
    env_wrapper=dict(
        suite='FullTown02-v1',
    ),
    server=[dict(
        carla_host='localhost',
        carla_ports=[9000, 9002, 2]
    )],
    eval=dict(
        render=True,
    ),
)

main_config = EasyDict(eval_config)


def main(cfg, seed=0):
    cfg.policy = deep_merge_dicts(PPOPolicy.default_config(), cfg.policy)

    tcp_list = parse_carla_tcp(cfg.server)
    host, port = tcp_list[0]

    carla_env = DiscreteBenchmarkEnvWrapper(SimpleCarlaEnv(cfg.env, host, port), cfg.env_wrapper)
    carla_env.seed(seed)
    set_pkg_seed(seed)
    model = PPORLModel(**cfg.model)
    policy = PPOPolicy(cfg.policy, model=model)

    if cfg.policy.ckpt_path != '':
        state_dict = torch.load(cfg.policy.ckpt_path, map_location='cpu')
        policy.eval_mode.load_state_dict(state_dict)
    evaluator = SingleCarlaEvaluator(cfg.eval, carla_env, policy.eval_mode)
    for i in range(10):
        evaluator.eval()
    evaluator.close()


if __name__ == '__main__':
    main(main_config)

import numpy as np
from sb3_contrib import TQC
from Env_fiber_simulated_goal import *
from CustomTensorboardCallback import *
import pandas as pd


def main():
    neutralxm1 = (max_xm1 - min_xm1) * params[0] + min_xm1
    neutralym1 = (max_ym1 - min_ym1) * params[2] + min_ym1
    neutralxm2 = (max_xm2 - min_xm2) * params[4] + min_xm2
    neutralym2 = (max_ym2 - min_ym2) * params[6] + min_ym2
    startvalues_mean = np.array([neutralxm1, neutralym1, neutralxm2, neutralym2], dtype=int)
    min_actuators_grid_scan = np.array([min_xm1, min_ym1, min_xm2, min_ym2])
    max_actuators_grid_scan = np.array([max_xm1, max_ym1, max_xm2, max_ym2])
    initial_radius = 109227
    min_power = 0.05
    number_obs_saved = 4
    max_actioninsteps = 6 * 10 ** 3
    minmirrorintervalsteps = 3 * 10 ** 6
    maxmirrorintervalsteps = 7 * 10 ** 6
    reset_power_fail = 0.2
    reset_power_goal = 0.8
    reset_step_size = 10 ** 3
    min_power_after_reset = 0.4
    max_power_after_reset = reset_power_goal
    max_random_reset_step = 10 ** 3
    min_actioninsteps = 1
    max_power_to_neutral = 0.04
    number_of_random_steps_low_power = 10
    min_power_stop_random_steps = 0.04
    max_random_reset_step_low_power = 10 ** 4
    max_random_reset_step_high_power = 10 * max_random_reset_step
    max_episode_steps = 20
    reset_method = "move_power_up"

    number_tries = 100

    beta_step = 5
    beta_fail_1 = 5
    beta_fail_2 = 5
    alpha_fail = 0.9
    alpha_step = 0.5
    prefactor_step = 10
    prefactor_goal = 100
    prefactor_fail = 10

    save_name = (f"TQC_reward_2024_04_22_betas_step_{beta_step}_fail_{beta_fail_1}"
                 f"_{beta_fail_2}_alphas_step_{alpha_step}_fail_{alpha_fail}_prefactors_{prefactor_step}"
                 f"_{prefactor_fail}_{prefactor_goal}"
                 f"_hyperparameter_search_goal.csv")
    if os.path.exists(save_name):
        df = pd.read_csv(save_name, index_col=0)
    else:
        df = pd.DataFrame(data=None, index=None,
                      columns=["beta_goal_1", "beta_goal_2", "alpha_goal", "timestamp",
                               "number_timesteps", "percentage_in_goal", "percentage_failed",
                               "P_max_episode_steps_ave"])
    # test different alphas, betas goal reward
    a_list = [[0.9, 1, 1], [0.9, 1, 5], [0.9, 5, 1]]
    for _ in range(5):
        for a in a_list:
            beta_goal_1 = a[1]
            beta_goal_2 = a[2]
            alpha_goal = a[0]
            reward_fct_descriptor_2024_04_22 = (
                f"reward_2024_04_22_betas_{beta_step}_{beta_fail_1}_{beta_fail_2}"
                f"_{beta_goal_1}_{beta_goal_2}_prefactor_{prefactor_step}_"
                f"{prefactor_fail}_{prefactor_goal}_alphas_{alpha_step}_{alpha_fail}_{alpha_goal}")

            def reward_fct_2024_04_22(avg_power, max_power, power, reset_power_fail, max_episode_steps,
                                      reset_power_goal, min_power_after_reset, current_step):
                if power > reset_power_goal:
                    reward = prefactor_goal * (
                            ((1 - alpha_goal) * np.exp(-beta_goal_1 * current_step / max_episode_steps))
                            + alpha_goal * np.exp(beta_goal_2 * power / reset_power_goal))
                elif power < reset_power_fail:
                    reward = - prefactor_fail * (
                            (1 - alpha_fail) * np.exp(-beta_fail_1 * current_step / max_episode_steps)
                            + alpha_fail * np.exp(-beta_fail_2 * power / reset_power_fail))
                else:
                    reward = prefactor_step / max_episode_steps * ((1 - alpha_step) * np.exp(
                        beta_step * (power - reset_power_goal)) + alpha_step * (power - min_power_after_reset))
                return reward

            env = Env_fiber_simulated(max_actioninsteps, minmirrorintervalsteps, maxmirrorintervalsteps,
                                      min_actuators_grid_scan,
                                      max_actuators_grid_scan, startvalues_mean, initial_radius,
                                      reset_power_fail,
                                      reset_power_goal, reward_fct_2024_04_22,
                                      reward_fct_descriptor_2024_04_22,
                                      max_random_reset_step_high_power, max_random_reset_step_low_power,
                                      min_power_stop_random_steps, max_power_to_neutral,
                                      number_of_random_steps_low_power, reset_step_size,
                                      min_power_after_reset, max_power_after_reset, min_power, reset_method,
                                      max_steps_under_min_power=3,
                                      average_over=10, number_obs_saved=number_obs_saved,
                                      max_episode_steps=max_episode_steps,
                                      timestamp=None,
                                      random_reset=True, dir_names=None, save_replay=True)
            env.reset()
            timestamp = env.timestamp

            num = 0
            # new TQC model
            policy_kwargs = dict(n_critics=2, n_quantiles=25)
            model = TQC("MlpPolicy", env, top_quantiles_to_drop_per_net=2, verbose=1,
                        policy_kwargs=policy_kwargs, tensorboard_log=env.logdir)
            TIMESTEPS = 10000
            # test start model
            percentage_in_goal, percentage_failed, P_max_episode_steps_ave = 0.0, 0.0, 0.0
            for j in range(number_tries):
                obs, info = env.reset()
                terminated = False
                truncated = False
                while not (terminated or truncated):
                    action, _states = model.predict(obs)
                    obs, rewards, terminated, truncated, info = env.step(action)
                P_max_episode_steps_ave += obs[-1] / number_tries
                if env.goal:
                    percentage_in_goal += 1 / number_tries
                if env.fail:
                    percentage_failed += 1 / number_tries
            df = pd.concat([df, pd.DataFrame([[beta_goal_1, beta_goal_2, alpha_goal,
                                               timestamp, num, percentage_in_goal, percentage_failed,
                                               P_max_episode_steps_ave]], columns=df.columns)],
                           ignore_index=True)
            df.to_csv(save_name)
            for i in range(10):
                # train for 10k steps
                model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="TQC",
                            callback=CustomTensorboardCallback(env), progress_bar=True)
                model.save(f"{env.models_dir}/{num + TIMESTEPS * (i + 1)}")
                # test current model
                percentage_in_goal, percentage_failed, P_max_episode_steps_ave = 0.0, 0.0, 0.0
                for j in range(number_tries):
                    obs, info = env.reset()
                    terminated = False
                    truncated = False
                    while not (terminated or truncated):
                        action, _states = model.predict(obs)
                        obs, rewards, terminated, truncated, info = env.step(action)
                    P_max_episode_steps_ave += obs[-1] / number_tries
                    if env.goal:
                        percentage_in_goal += 1 / number_tries
                    if env.fail:
                        percentage_failed += 1 / number_tries
                df = pd.concat([df, pd.DataFrame([[beta_goal_1, beta_goal_2, alpha_goal,
                                                        timestamp, num + TIMESTEPS * (i + 1), percentage_in_goal,
                                                        percentage_failed,
                                                        P_max_episode_steps_ave]], columns=df.columns)],
                                    ignore_index=True)
                df.to_csv(save_name)


if __name__ == '__main__':
    main()
import subprocess
import os




def run_snowpack(config_path: str, config_name:str, data_path: str, output_path: str,end_date:str = "2025-06-1T0:00"):
    config_path = os.path.abspath(config_path)
    data_path = os.path.abspath(data_path)
    output_path = os.path.abspath(output_path)
    
    print("Using configuration from:", config_path)
    print("Using data from:", data_path)
    print("Output will be saved to:", output_path)
    print('---------------------------------------------------------------')

    command = [
        "docker", "run", "--rm",
        "-v", f"{config_path}:/config_to_test:ro",
        "-v", f"{data_path}:/data:ro",
        "-v", f"{output_path}:/output",
        "snowpack-env",
        "snowpack", "-c", f"/config_to_test/{config_name}","-e", f"{end_date}"
    ]

    print("Running command:", " ".join(command))
    subprocess.run(command, check=True)

if __name__ == "__main__":
    config_folder = "./config_to_test"
    for config_file in os.listdir(config_folder):
        if config_file.endswith(".ini"):
            run_snowpack(
                config_path=config_folder,
                config_name=config_file,
                data_path="./data",
                output_path="./output"
            )

#parallelized
"""
def run_snowpack_parallelized():
    num_jobs = 4  # Number of parallel jobs
    base_path = Path(".")

    # Each job uses its own config, data, and output directory
    jobs = [
        (
            f"./configs/job{i}",
            f"./data/job{i}",
            f"./output/job{i}",
            f"job{i}"
        )
        for i in range(num_jobs)
    ]

    with ThreadPoolExecutor(max_workers=num_jobs) as executor:
        futures = [
            executor.submit(run_snowpack, cfg, dat, out, tag)
            for cfg, dat, out, tag in jobs
        ]
        for f in futures:
            f.result()  # Wait for all jobs
"""
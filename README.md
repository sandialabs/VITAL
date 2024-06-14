# Setting up Python Environment using Conda

This guide will walk you through the process of setting up a Python environment using Conda. 
The provided command will create an environment and activate it, allowing you to run the tutorial or any other code within this environment.

## Prerequisites
- Conda should be installed on your system.
- If you don't have Conda installed, you can download it from the official Conda website: [https://www.anaconda.com/download](https://www.anaconda.com/download)

### Resources

- [Anaconda Introduction]([resource1_link](https://anaconda.cloud/video-gs-installing-anaconda-windows)) - This link contains a helpful guide for first-time Python users. It guides the user through installing Anaconda on Windows (and Mac). Other videos in the tutorial sequence also provide an overview of what Python is, what Anaconda is, and what Jupyter Notebook is, among others.

## Instructions

1. Clone or download this repository.

2. Open a terminal or command prompt and navigate to the project directory.

3. Run the following command to create the Conda environment:
```
conda env create --file environment.yml
```

This command will install all the required packages listed in the `environment.yml` file. Please note that the installation process might take some time, as Conda will download and install the necessary packages.

4. Once the environment creation process is complete, activate the environment using the following command:
```
conda activate HDPS
```

This command will activate the newly created environment named "HDPS". You should see the environment name in your terminal prompt.

5. You have successfully set up the Python environment using Conda! Now you can run the tutorial within this environment.

## Additional Notes

- If you need to deactivate the environment, you can use the following command:

```
conda deactivate
```
- Remember to activate the environment again using `conda activate HDPS` whenever you want to work within this environment.

- If you want to remove the environment, you can use the following command:
```
conda env remove --name HDPS
```

This command will remove the "HDPS" environment and all its associated packages.


# Launching Jupyter Notebook from the Command Line
## Instructions

1. Open a terminal or command prompt.

2. Activate the "HDPS" Conda environment using the following command:
```
conda activate HDPS
```
This command will activate the "HDPS" environment, ensuring that you are using the correct Python environment for running Jupyter Notebook.

3. Navigate to the directory where you want to create or open your Jupyter Notebook.

4. Run the following command to launch Jupyter Notebook:
```
jupyter notebook
```

This command will start the Jupyter Notebook server and open a new tab or window in your default web browser.

5. In the Jupyter Notebook interface, you can create a new notebook or open an existing notebook by clicking on the respective options.

6. You can now start working with Jupyter Notebook and run the tutorials available in this GitHub repository.

7. To stop the Jupyter Notebook server, go back to the terminal or command prompt where it was launched and press `Ctrl + C`. Confirm by typing `y` and pressing `Enter`.


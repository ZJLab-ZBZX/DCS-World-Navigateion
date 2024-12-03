It is a demo task using DCS world. We train a Soft Actor-Critic (SAC) agent to navigate to a randomly chosen destination in each run. 


##  Usage
1. Install requirements.txt.
2. Copy Scripts/Export.lua to C:\Users\<name>\Saved Games\DCS\Scripts. Infer your own UDP address and replace the one in Export.lua with it, i.e., host = "239.255.50.10".
3. Copy Missions/navi.miz to C:\Users\<name>\Saved Games\DCS\Missions.
4. Copy BriefingDialog.lua and GameMenu.lua to D:\Program Files\Eagle Dynamics\DCS World\Scripts\UI. It will replace the files with the same names.
5. Open the DCS-world game and start the navigation task.  i.e., *mission --> navi*.
6. Run the learning script with
    ```
    $ python train_dcs_gym.py
    ```


## Acknowledgement
If you use this toolkit in your research, please cite it as follows:
```latex
@misc{ZJ2024DataProcessesToolkit,
 author = {Zhejiang Lab},
 title = {DCS-World-Navigateion},
 year = {2024},
 howpublished = {\url{https://github.com/ZJLab-ZBZX/DCS-World-Navigateion}},
 note = {Accessed: 2024-11-19}
}
```

## Contact us
If you have any problems using the toolkit, please contact us via email at hongmingli1995@gmail.com

© 2024 Research Center for Intelligent Equipment of Zhejiang Lab

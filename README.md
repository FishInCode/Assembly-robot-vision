# Assembly Robot: Vision-Guided 4-DOF Manipulation

## Project Overview
A vision-guided assembly system designed for the **Zhejiang Provincial Undergraduate Robotics Competition**. The robot identifies workpieces on a conveyor belt, locates target holes on a rotating disc, and controls a 4-DOF robotic arm to assemble them.

### Tech Stack
*   **Software:** Python, C++, YOLOv5, OpenCV
*   **Edge Device:** MaixCam (RISC-V embedded vision module)
*   **Hardware:** 4-DOF Robotic Arm, Microcontrollers, UART

---

## My Core Contributions
*   **System Optimization under Constraints:** The original design required 3 cameras for workpieces, holes, and gripper pose. To overcome hardware limits, I redesigned the vision pipeline using only 2 cameras, combining workpiece recognition and hole localization.
*   **Visual Recognition Pipeline:** Developed MaixCam-based routines using **YOLOv5** for object detection and **LAB color thresholding** for component recognition and image-based localization.
*   **Hardware-Software Integration:** Converted image coordinates into robotic-arm motion parameters. Engineered **UART command protocols** to transmit position data between the MaixCam and embedded controllers.

---

## Engineering Troubleshooting
*Real engineering is about solving unexpected problems.*

*   **Model Confusion (Square vs. Trapezoid):** YOLOv5 sometimes failed to differentiate between a square and a trapezoid. I added a **rectangular contour detection** step and compared side lengths to assist the decision-making, which significantly improved the reliability of the arm's grasp.
*   **Grasping Offset:** Even with accurate recognition, the gripper occasionally missed the hole due to camera mounting offsets. I implemented position compensation parameters and tuned them iteratively for different shapes.

---

## Results & Achievements
*   **Awarded Third Prize** at the Zhejiang Provincial Undergraduate Robotics Competition (2025).
*   Successfully completed the end-to-end vision-communication-actuation integration, even with a constrained hardware setup.

---

## Acknowledgements
*   **Academic Advisors:** [填写指导老师名字] at [填写学校], for his valuable guidance on system integration.
*   **Team Members:** [填写队友名字], for their collaboration in mechanical design and integration testing.

---
*Maintained by FishInCode.*

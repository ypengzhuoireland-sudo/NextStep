**Meeting Minutes**

**Meeting Time:** June 28, 2026, 10:00–11:00
 **Meeting Format:** Zoom online meeting
 **Team Name:** NextStep

## 1. Main Discussion

This meeting was conducted online via Zoom. The team mainly discussed the questions raised by the professors on June 23, as well as the next steps for system improvement, user research, the AI assistant feature, and cloud deployment.

During the meeting, the team focused on one key question raised by the professors: if a new student enters the system without any previous exercise records, how can the system provide personalized exercise recommendations for that student? After discussion, the team agreed that for new users without exercise history, the system cannot directly evaluate their mastery of different Knowledge Components (KCs) based on past performance. Therefore, a **mock test** mechanism should be added before students formally enter the system.

The team plans to design a set of mock test questions. When a new student uses the system for the first time, they will be required to complete the mock test first. Based on the student’s performance in the mock test, the system will initially estimate their mastery level across different KCs. This result will then serve as the basis for later personalized exercise recommendations. In this way, the system can address the cold-start problem, quickly build an initial learning profile for new users, and provide a more reasonable practice path.

The team also discussed whether user research should be conducted later. The team believed that although the current prompt system and layered hints have already been basically implemented, it is still necessary to further verify whether these prompts are truly useful for students. Therefore, the team may conduct user surveys or collect simple feedback to analyse students’ understanding of the prompts, their evaluation of usefulness, and whether the prompts help them complete the exercises.

In addition, the team discussed the deployment of the system. The project will later be deployed on **Microsoft Azure**, so that the system can run more stably and be more convenient for demonstration, testing, and future access.

Finally, the team decided to add an **AI assistant** feature next week to further improve the user experience. When students encounter personalized questions during learning, they will be able to ask the AI assistant for help. The AI assistant will provide explanations, guidance, and support like a teacher, making up for the fact that fixed hints cannot cover every learning situation.

## 2. Decisions Made

### 1. Analysing the Questions Raised by the Professors

After discussion, the team confirmed that:

- The issue of new students having no previous exercise records needs to be addressed carefully;
- New users cannot receive personalized recommendations directly from historical data;
- The system needs to add a mock test as an initial assessment before new users enter the system;
- The mock test results will be used to estimate students’ initial mastery of different KCs;
- Future exercise recommendations will be adjusted based on the mock test results.

This decision provides a clear direction for solving the cold-start problem in the system and allows the system to better support first-time users.

### 2. Designing the Mock Test Mechanism

The team decided to design a mock test process later:

- New students need to complete a mock test when they first enter the system;
- The mock test will cover the main Knowledge Components;
- The system will estimate students’ mastery of different knowledge points based on their answers;
- The mock test results will be used as the basis for personalized recommendations and mastery initialization;
- After completing the mock test, students will formally enter the practice system.

This mechanism will help the system quickly establish a student’s learning status even when there is no historical record.

### 3. Considering User Research

The team believed that user research may be needed later to verify whether the prompts and AI feedback in the system are truly useful. The research may cover:

- Whether students can understand the prompts given by the system;
- Whether layered hints help students solve problems;
- Whether AI advice has learning-guidance value;
- Whether students believe these functions improve their learning experience.

Through user research, the team can further improve the prompt design and make the system more suitable for real learning scenarios.

### 4. Deployment on Microsoft Azure

The team confirmed that the project will later be deployed on Microsoft Azure. After deployment, the system will be more convenient for demonstration, testing, and access, and it will also improve the overall completeness and professionalism of the project.

### 5. Adding an AI Assistant Feature

The team decided to add an AI assistant feature next week to further improve the user experience. The goals of this feature are:

- To allow students to ask their own personalized questions;
- To enable the AI assistant to provide explanations and guidance based on the questions;
- To help students like a teacher when they encounter difficulties;
- To complement the scenarios that layered hints and AI advice cannot fully cover.

The team believes that the AI assistant can improve the interactivity and intelligence of the system, making NextStep closer to a real adaptive learning platform.
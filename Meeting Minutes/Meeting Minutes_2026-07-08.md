# Meeting Minutes

**Meeting Time:** 8 July 2026, 10:00–10:30
 **Meeting Format:** Online meeting via Zoom
 **Team Name:** NextStep

## 1. Main Meeting Content

This meeting was conducted online via Zoom. The discussion mainly focused on the optimisation of the AI assistant function, the permission issue of the KC heatmap, the design of the mock test mechanism, and the follow-up task allocation. The team reached the following decisions.

During the meeting, the team first discussed the existing problems with the current AI assistant function. After testing, the team found that the AI assistant is still not intelligent enough. Its main limitation is that when students ask questions, the AI assistant can only provide simple guidance or redirect students to relevant exercises. It is not yet able to provide deeper and more personalised explanations or support based on students’ specific learning situations. Therefore, the team decided that the AI assistant function needs to be further modified and optimised so that it can better support students’ learning. This part will be handled by **Xia Linjie**.

Afterwards, the team discovered a permission display issue in the system: student users were able to view everyone’s KC heatmap. After discussion, the team agreed that this does not meet the requirements of user permission control. The system should ensure that students can only view their own KC mastery status and should not be able to see other students’ data. Only teacher accounts should be able to view all students’ KC heatmap information after logging in. This issue has been confirmed by the team and will be fixed by **Yu Zihan**, who will adjust the related frontend or permission display logic.

In addition, the team continued to discuss the issue of personalised recommendations for new users. Since some students may not have any exercise history when they first enter the system, the system cannot directly judge their KC mastery based on past performance. To solve this problem, the team plans to design a **mock test** mechanism for students without history records. When students use the system for the first time, they will need to complete a mock test first. The system will then use their answers in the mock test to make an initial judgement of their mastery across different KCs and use this information to provide more personalised exercise recommendations and learning services. This task will be completed by **Wang Kaijun** and **Zhuo Yupeng**.

## 2. Meeting Decisions

1. **Optimise the AI assistant function**
    The current AI assistant is not intelligent enough and can only redirect students to exercises in a relatively simple way. It needs to be further modified so that it can provide more effective explanations, guidance, and support based on students’ questions.
    **Responsible Person:** Xia Linjie
2. **Fix the KC heatmap permission display issue**
    At present, students can view everyone’s KC heatmap. This permission setting needs to be changed. After modification, students will only be able to view their own KC heatmap, while teachers will be able to view all students’ KC heatmaps after logging in.
    **Responsible Person:** Yu Zihan
3. **Set up a mock test for new students without history records**
    For new students who do not have any exercise history, the system will use a mock test to collect their initial performance and judge their KC mastery based on the results. This will provide a basis for later personalised recommendations.
    **Responsible Persons:** Wang Kaijun and Zhuo Yupeng

## 3. Follow-up Task Allocation

| Task                                                         | Responsible Person          |
| ------------------------------------------------------------ | --------------------------- |
| Modify and optimise the AI assistant function so that it does not only redirect students to exercises | Xia Linjie                  |
| Modify the KC heatmap permission display logic to ensure that students can only see their own data | Yu Zihan                    |
| Design and implement the mock test mechanism for assessing students without history records | Wang Kaijun and Zhuo Yupeng |

## 4. Meeting Summary

This meeting mainly focused on the issues discovered during system testing and clarified the direction for follow-up optimisation. The team agreed that the AI assistant, KC heatmap permission control, and mock test mechanism are all important parts that affect the user experience and the effectiveness of personalised recommendations. The team will continue to work on these functions according to the task allocation agreed in this meeting, in order to improve the completeness, rationality, and practicality of the system.
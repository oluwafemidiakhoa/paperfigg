# Sample Paper

## 1 Methodology
We propose a three-stage pipeline: preprocess data, encode observations, and decode outputs.
The method uses attention and residual links.

## 2 System Architecture
The system has four modules: parser, planner, generator, and critic.
Data flows from parser to planner, planner to generator, and generator to critic.

## 3 Results
Our model improves F1 score from 0.81 to 0.88 on benchmark A and from 0.76 to 0.84 on benchmark B.
Ablation indicates the planner module contributes most.

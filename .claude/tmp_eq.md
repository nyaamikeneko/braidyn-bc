### JOINT
 session s can be written
638
ECLLs(Θ) ≡
X
zs
p
zs|Ds, Θold
log p
ys, zs|Θ, {xs,t}Ts
t=1

=
K
X
k=1
γs,1,k log πk +
Ts
X
t=1
K
X
j=1
K
X
k=1
ξs,t,j,k log Ajk +
Ts
X
t=1
K
X
k=1
γs,t,k log p(ys,t|zs,t = k, xs,t, wk)
(7)
In order to get to the second line, we substituted the definition of the joint distribution for the GLM-HMM:
639
p(ys, zs|{xs,t}Ts
t=1, Θ) ≡p(z1)p(y1|z1, x1)
Ts
Y
t=2
p(zt|zt-1)p(yt|zt, xt).
(8)
In Eq. 7, p(ys,t|zs,t = k, xs,t, wk) is the Bernoulli GLM distribution given by Eq. 4. Finally,
640
γs,t,k ≡p
zs,t = k|Ds, Θold
(9)
.
CC-BY 4.0 International license
perpetuity. It is made available under a 
preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in 
The copyright holder for this
this version posted December 13, 2021. 
; 
https://doi.org/10.1101/2020.10.19.346353
doi: 
bioRxiv preprint 

==================== PAGE 17 ====================
17
is the posterior state probability at trial t (in session s) for state k, while
641
ξs,t,j,k ≡p
zs,t+1 = k|zs,t = j, Ds, Θold
(10)
is the joint posterior state distribution for two consecutive latents.
642
While the formula for the log posterior (Eq. 5) involved the sum over all possible state assignments at
643
each trial, by taking advantage of the structure of the joint probability distribution for the GLM-HMM
644
(Eq. 8), this sum was implemented efficiently and Eq. 7 involves summing over at most O(K2Ts) ele-
645
ments.
646
The single and joint posterior state probabilities, γs,t,k and ξs,t,k, are estimated via the forward-backward
64

### ALG
 Θ ≡{π, A, {wk}K
k=1}, are learned directly from each animal’s choice data via the EM
118
algorithm described in Section 4.1.
119
It is worth noting that the classic lapse model described in Eq. 1 and Eq. 2 corresponds to a restricted
120
2-state GLM-HMM. If we consider state 1 to be “engaged” and state 2 to be the “lapse” state, then the
121
state-1 GLM has weights w1 =w, and the state-2 GLM has all weights set to 0 except the bias weight,
122
which is equal to -log(γl/γr). The transition matrix has identical rows, with probability 1 -(γr + γl)
123
of going into state 1 and probability (γr + γl) of going into state 2 at the next trial, regardless of the
124
current state. This ensures that the probability of a lapse on any given trial is stimulus-independent and
125
does not depend on the previous trial’s state. Fig. 1a-c shows an illustration of the classic lapse model
126
formulated as a 2-state GLM-HMM.
127
However, there is no general reason to limit our analyses to this restricted form of the GLM-HMM.
128
By allowing the model to have more than two states, multiple states with non-zero stimulus weights,
129
and transition probabilities that depend on the current state, we obtain a model family with a far richer
130
set of dynamic decision-making behaviors. Fig. 1d shows an example GLM-HMM with three latent
131
states, all of which have high probability of persisting for multiple trials. Intriguingly, the psychometric
132
curve arising from this model (Fig. 1f) is indistinguishable from that of the classic lapse model. Thus,
133
multiple generative processes can result in identical psychometric curves, and we must look beyond
134
the psychometric curve if we want to gain insight into the dynamics of decision-making across trials.
135
2.3
Mice switch between multiple strategies.
136
To examine whether animals employ multiple strategies during decision-making, we fit the GLM-HMM
137
to behavioral data from two binary perceptual decision-making tasks (see Methods 4.1). First, we fit the
138
GLM-HMM to choice data from 37 mice performing a visual detection decision-making task developed in
139
[33] and adopted by the International Brain Laboratory (IBL) [19]. During the task, a sinusoidal grating
140
with contrast between 0 and 100% appeared either on the left or right side of the screen (Fig. 2a).
141
The mouse had to indicate this side by turning a wheel. If the mouse turned the wheel in the correct
142
direction, it received a water reward; if incorrect, it received a noise burst and an additional 1-second
143
timeout. During the first 90 trials of each session, the stimulus appeared randomly on the left or right
144
side of the screen with probability 0.5. Subsequent trials were generated in blocks in which the stimulus
145
appeared on one side with probability 0.8, alternating randomly every 20-100 trials. We analyzed data
146
from animals with at least 3000 trials of data (across multiple sessions) after they had successfully
147
learned the task (see Fig. S1, Fig. S2). For each animal, we considered only the data from the first 90
148
trials of each session, when the stimulus was equally likely to appear on the left or right of the screen.
149
We modeled the animals’ decision-making strategies using a GLM-HMM with four inputs: (1) the
150
(signed) stimulus contrast, where positive values indicate a right-side grating and negative values indi-
151
.
CC-BY 4.0 International license
perpetuity. It is made available under a 
preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in 
The copyright holder for this
this version posted December 13, 2021. 
; 
https://doi.org/10.1101/2020.10.19.346353
doi: 
bioRxiv preprint 

==================== PAGE 16 ====================
16
The prior distribution over the model parameters p(Θ) that we used was:
613
p(Θ) ≡p({wk})p(A)p(π) =


K
Y
j=1
N(wj|0, σ2I)




K
Y
j=1
Dirichlet(Aj|α)

Dirichlet(π|απ).
(6)
The prior over the GLM weight vectors wk was thus an independent, zero-mean Gaussian with variance


### CONCAT
 animals to one another. As such, we employed a multistage
684
fitting procedure that allowed us to make this comparison, and we detail this procedure in Algorithm 1.
685
In the first stage, we concatenated the data for all animals in a single dataset together (for the IBL
686
dataset, this would be the data for all 37 animals). We then fit a GLM (a 1 state GLM-HMM) to the
687
concatenated data using Maximum Likelihood estimation. We used the fit GLM weights to initialize the
688
GLM weights of a K-state GLM-HMM that we again fit to the concatenated dataset from all animals
689
together (to obtain a “global fit”). We added Gaussian noise with σinit = 0.2 to the GLM weights, so
690
.
CC-BY 4.0 International license
perpetuity. It is made available under a 
preprint (which was not certified by peer review) is the author/funder, who has granted bioRxiv a license to display the preprint in 
The copyright holder for this
this version posted December 13, 2021. 
; 
https://doi.org/10.1101/2020.10.19.346353
doi: 
bioRxiv preprint 

==================== PAGE 19 ====================
19
that the initialized states were distinct, and we initialized the transition matrix of the K-State GLM-HMM
691
as 0.95 × 1 + N(0, Σtrans.) where Σtrans. ∈RK2×K2 and Σtrans. = 0.05 × 1. We then normalized this
692
so that that rows of the transition matrix added up to 1, and represented probabilities. While the EM
693
algorithm is guaranteed to converge to a local optimum in the log probability landscape of Eq. 5, there
694
is no guarantee that it will converge to the global optimum [70]. Correspondingly, for each value of K,
695
we fit the model 20 times using 20 different initializations.
696
In the next stage of the fitting procedure, we wanted to obtain a separate GLM-HMM fit for each animal,
697
so we initialized a model for each animal with the GLM-HMM global fit parameters from all animals
698
together (out of the 20 initializations, we chose the model that resulted in the best training set log-
699
likelihood). We then ran the EM algorithm to convergence; it is these recovered parameters that are
700
shown in Fig. 4 and Fig. 5. By initializing each individual animal’s model with the parameters from the
701
fit to all animals together, it was no longer necessary for us to permute the retrieved states from each
702
animal so as to map semantically similar states to one another.
703
Algorithm 1 Multistage GLM-HMM fitting procedure
1: Fit GLM (1 state GLM-HMM) to all data from all animals
2: Fit global GLM-HMM to all data from all animals:
3: for K ∈{2, ..., 5} do
4:
for init. ∈{1, ..., 20} do
5:
Initialize K-state GLM-HMM using noisy GLM weights
6:
Run EM algorithm until conve
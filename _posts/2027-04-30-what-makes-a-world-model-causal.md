---
layout: distill
title: What Makes a World Model Causal?
description: What are world models, how do different objectives shape them, and when do predictions justify interventions, counterfactuals, or component reuse? A component-level account.
date: 2027-04-30
future: true
authors:
  - name: Anonymous
bibliography: 2027-04-30-what-makes-a-world-model-causal.bib
toc:
  - name: What are world models?
  - name: How do world models learn?
  - name: Formalising a causal world model
  - name: From representation to relational discovery
  - name: From prediction to causation
  - name: Identifiability is relative to the question
  - name: Can world-model components be reused?
  - name: What should we ask of a causal world model?
---
<!-- PRE-SUBMISSION (anonymity): Figures 1 and 3 are downscaled copies of artwork in
     Foundations-and-Trends-Causal-World-Models/nowfnt/figures/. If those figures appear
     in a named public preprint, redraw them before anonymous submission. See README. -->

## What are world models?

An agent rarely gets to try every possible action before making a decision. It must anticipate how its environment might change, often from incomplete observations. A **world model** is an internal model of environmental regularities that supports such anticipation: predicting what might happen next, simulating candidate trajectories, or supplying information for planning. The idea is longstanding in model-based reinforcement learning and has taken new forms in learned visual, latent, and generative dynamics <d-cite key="moerland2023model,ha2018world,hafner2025dreamer,lecun2022path"></d-cite>.

There is no single required architecture. Some models predict observations, including video frames or tokens; some predict compressed representations; others learn action-conditioned transitions or planning-relevant quantities without reconstructing the visible world <d-cite key="ha2018world,schrittwieser2020mastering,hansen2024tdmpc,assran2025vjepa2"></d-cite>. A latent representation may be useful even if its coordinates have no immediately interpretable meaning. The shared aim is *anticipation*; the models differ in **what they retain** and **which downstream questions they can answer**.

Imagine a robot arm facing two blocks on a table—one red and one blue—alongside a marked goal region. A video predictor might render the next frame. A dynamics model might estimate where the blocks move after a push. A planner might choose the push that moves the red block into the goal. But after an unexpected collision, could the model answer what *would have happened in that same episode* had the blue block been pushed instead? Predicting, acting, and reasoning about alternative outcomes are related capabilities—not interchangeable ones <d-cite key="pearl2009causality,bareinboim2022on"></d-cite>.

This leads to a more productive question than whether a system deserves the label *world model*: **What does it represent, what learning signal shaped that representation, and what causal or reuse claims do its evidence and assumptions actually justify?**

## How do world models learn?

Three **overlapping perspectives** organise much of the literature. They are not mutually exclusive architectures: masked reconstruction, contrastive objectives, entity decomposition, relational prediction, and interventional supervision can be layered across them. Nor do they sit at the same mathematical level: autoregression is a predictive factorisation, JEPA is a representation-predictive approach, and decision-oriented training specifies what the model should be useful *for* <d-cite key="lecun2022path,moerland2023model,locatello2020object"></d-cite>.

**1. Predict observations.** Autoregressive and generative objectives learn to anticipate the next token, frame, or observation:

$$
\mathcal{L}_{\mathrm{obs}}(\theta) = -\mathbb{E}_{\mathcal{D}}\!\left[\log \mathbb{P}_\theta(\mathbf{x}_{t+1} \mid \mathbf{x}_{\le t}, \mathbf{a}_{\le t})\right].
$$

This rewards observable predictive accuracy, which can induce internal features capturing motion, object persistence, and context. However, multiple latent organisations can realise the exact same observed distribution, so predictive fit does **not** uniquely determine which hidden entities or mechanisms produced the data <d-cite key="ha2018world,locatello2019challenging,khemakhem2020variational,kivva2022identifiability"></d-cite>.

**2. Predict representations.** Joint-Embedding Predictive Architectures (JEPAs), video JEPAs, and feature-space world models predict or align learned embeddings instead of reconstructing pixels <d-cite key="lecun2022path,assran2025vjepa2,zhou2025dinowm,balestriero2025lejepa"></d-cite>. Schematically, a latent predictor $$F_\theta$$ matches a target embedding:

$$
\mathcal{L}_{\mathrm{repr}} = \mathbb{E}\!\left[d\!\left(F_\theta(f_\theta(\mathbf{x}_t), \mathbf{a}_t),\,\operatorname{sg}[f_{\bar\theta}(\mathbf{x}_{t+1})]\right)\right] + \lambda_{\mathrm{nc}}\Omega_{\mathrm{nc}},
$$

with architecture-specific anti-collapse regularisation $$\Omega_{\mathrm{nc}}$$ (for example, stop-gradient/EMA targets in V-JEPA 2 or sketched isotropic Gaussian regularisation in LeJEPA). Invariance ($$f(T\mathbf{x})=f(\mathbf{x})$$) and equivariance ($$f(T\mathbf{x})=T'f(\mathbf{x})$$) constrain which transformations are ignored or tracked. Even when representation recovery theorems hold—such as linear or orthogonal recovery for LeJEPA under stationary additive-noise assumptions <d-cite key="klindt2026when"></d-cite>—they do not automatically yield entity-attribute separation, causal graphs, or interventional semantics <d-cite key="scholkopf2021toward,locatello2019challenging"></d-cite>. Similarly, object-level latent masking (as in Causal-JEPA <d-cite key="namcausal"></d-cite>) changes the predictor's *observability* of a slot; it does not physically remove an object or establish the effect of a structural intervention.

**3. Learn for decisions.** In model-based reinforcement learning, latent dynamics are trained jointly with reward, value, or policy objectives. Dreamer imagines trajectories for policy optimisation; MuZero learns planning-relevant reward, value, and policy predictions without observation reconstruction; TD-MPC2 combines latent dynamics with control <d-cite key="hafner2025dreamer,schrittwieser2020mastering,hansen2024tdmpc"></d-cite>. Value-equivalent models show why two distinct internal dynamics can remain equally adequate for a chosen planning computation <d-cite key="grimm2020value"></d-cite>. Conversely, while sufficiently rich policy competence across many tasks or local shifts can informationally determine transition or causal structure under strong oracle assumptions <d-cite key="richens2024robust,richens2025general"></d-cite>, one successful trained policy on a fixed task does not identify entities, causal relations, or unsupported action effects.

Crucially, **model-construction scores** (such as $$\mathcal{L}_{\mathrm{obs}}$$ or $$\mathcal{L}_{\mathrm{repr}}$$) are distinct from **environmental task utility** $$\mathcal{U}$$: the former specifies what training rewards, while the latter evaluates physical outcomes in the world. Across all three perspectives, three concepts must be kept separate:

$$
\underbrace{\text{objective}}_{\text{what encourages emergence}}
\;\neq\;
\underbrace{\text{component}}_{\text{where it is represented}}
\;\neq\;
\underbrace{\text{guarantee}}_{\text{what is identifiable}}.
$$

| Model family / example | Primary learning signal & components | Supported queries | What remains unconstrained for causal reuse |
|---|---|---|---|
| **Generative latent dynamics** (e.g., Dreamer <d-cite key="hafner2025dreamer"></d-cite>) | Observation/reward prediction + latent dynamics | Predictive rollouts, task policy learning | Entity identities, causal graph, unsupported action effects |
| **Decision-focused dynamics** (e.g., MuZero, TD-MPC2 <d-cite key="schrittwieser2020mastering,hansen2024tdmpc"></d-cite>) | Reward, value, and policy prediction in latent space | Planning for the training task family | Observation decoding, named causal factors; new rewards may need discarded distinctions |
| **Joint-embedding prediction** (e.g., V-JEPA 2, LeJEPA, Causal-JEPA <d-cite key="assran2025vjepa2,balestriero2025lejepa,klindt2026when,namcausal"></d-cite>) | Latent alignment + anti-collapse or object-level masking | Feature prediction, representation reuse, planning | Action semantics, confounding adjustment, structural counterfactual coupling |
| **Object-centric encoders** (e.g., Slot Attention <d-cite key="locatello2020object"></d-cite>) | Permutation-equivariant spatial grouping | Entity-structured representations | Architectural symmetry $$\neq$$ physical entity/attribute identifiability or unseen compositions |
| **Identifiable representation models** (e.g., iVAE, GMM/additive decoders <d-cite key="khemakhem2020variational,kivva2022identifiability,lachapelle2024additive"></d-cite>) | Auxiliary conditioning, mixture priors, or additive decoders | Latent laws or blocks up to affine/block maps | Named semantic anchors, causal graph directions, operational action targets |

## Formalising a causal world model

A generic predictive world model may be an opaque function of observation history. For a *reusable* Causal World Model (CWM), we propose explicit component interfaces connecting observations, entities, relations, actions, dynamics, and utility. This is a **component-level specification**, not a universal restriction imposed on every world-model architecture.

We write bold symbols for random variables ($$\mathbf{x}_t, \mathbf{v}_t, \mathbf{r}_t, \mathbf{a}_t$$) and plain symbols for their realised values ($$x_t, v_t, r_t, a_t$$). At time $$t$$, an agent observes $$\mathbf{x}_t \in \mathcal{X}$$ and may take an action $$\mathbf{a}_t \in \mathcal{A}$$. For a set of represented entities $$O_t$$, an encoder $$\phi$$ infers entity-indexed attributes $$\mathbf{v}_t = (\mathbf{v}_t^i)_{i \in O_t}$$, and an assembly map $$\psi_{O_t}$$ constructs a **structured relational state** $$\mathbf{r}_t \in \mathcal{R}_{O_t}$$:

$$
\mathbf{x}_t \xrightarrow{\;\phi\;} \mathbf{v}_t \xrightarrow{\;\psi_{O_t}\;} \mathbf{r}_t = \psi_{O_t}(\mathbf{v}_t) = (\mathbf{v}_t, g(\mathbf{v}_t)).
$$

Concretely, the components $$\mathbf{r}_{m,t}^{i,j}$$ of $$\mathbf{r}_t$$ sit in a matrix-like layout over entity pairs $$i, j \in O_t$$:
- **Diagonal blocks ($$i = j$$)** store intra-entity attributes: $$\mathbf{r}_t^{i,i} \equiv \mathbf{v}_t^i$$ (for example, each block's colour, position, height, and shadow).
- **Off-diagonal blocks ($$i \neq j$$)** store inter-entity relations: $$\mathbf{r}_{m,t}^{i,j} = g_m^{i,j}(\mathbf{v}_t^i, \mathbf{v}_t^j)$$ (such as relative displacement, occlusion, or contact).

Crucially, $$\mathcal{R}_{O_t} := \psi_{O_t}(\mathcal{V}_{O_t})$$ contains only **feasible** combinations. If a relation specifies displacement $$d = p_{\mathrm{blue}} - p_{\mathrm{red}}$$, then a triple $$(p_{\mathrm{red}}, p_{\mathrm{blue}}, d) = (0, 1, 5)$$ is inadmissible. This makes $$\mathbf{r}_t$$ a constrained geometric and semantic interface rather than an arbitrary latent vector.

<div class="l-page">
  <img src="{{ '/assets/img/2027-04-30-what-makes-a-world-model-causal/tabletop-example.png' | relative_url }}" alt="Tabletop manipulation task illustrating the entity-centric causal pipeline from low-level pixels to per-entity latent states, pairwise relations, latent causal graph, actions, and environment transitions." style="width:100%;max-width:1100px;display:block;margin:auto;" />
</div>
<div class="caption"><strong>Figure 1.</strong> Tabletop manipulation example illustrating the abstraction \(\mathbf{x}_t \to \mathbf{v}_t \to \mathbf{r}_t \to \mathcal{G}_r\). Observations are encoded into per-entity attribute slots \(\mathbf{v}_t^i\) (diagonal entries \(i=j\) of \(\mathbf{r}_t\)), assembled with pairwise inter-entity relations (\(i \neq j\)), and connected to actions \(\mathbf{a}_t \in \mathcal{A}\) and environment transitions. The relation assembly is a representational constraint, not by itself an environmental causal mechanism.</div>

Collecting observation and relational state into the formal state $$\mathbf{s}_t = (\mathbf{x}_t, \mathbf{r}_t) \in \mathcal{S}$$, a component-level CWM is specified as the tuple

$$
\boxed{W = \bigl(\mathcal{X}, \mathcal{A}, \{\mathcal{R}_O\}_O, \mathbb{P}, \mathcal{U}\bigr)}, \qquad \mathcal{U} : \mathcal{A} \times \mathcal{S} \to \mathbb{R},
$$

where $$\mathbb{P}$$ is the joint probability law over successive formal states and actions in a given regime, and $$\mathcal{U}$$ evaluates actions and formal states. Under three **explicit conditional independences**—

1. $$\mathbf{x}_{t+1} \perp (\mathbf{x}_t, \mathbf{r}_t, \mathbf{a}_t) \mid \mathbf{r}_{t+1}$$ (updated state suffices to predict the next observation),
2. $$\mathbf{r}_{t+1} \perp \mathbf{x}_t \mid (\mathbf{r}_t, \mathbf{a}_t)$$ (current relational state and action retain what matters from $$\mathbf{x}_t$$ for the next state), and
3. $$\mathbf{r}_t \perp \mathbf{a}_t \mid \mathbf{x}_t$$ (observation-only inference: the logged action adds no information about $$\mathbf{r}_t$$ beyond $$\mathbf{x}_t$$),

the one-step observed predictive law factors into three explicit interfaces:<d-footnote>Because $$\mathbf{r}_t = (\mathbf{v}_t, g(\mathbf{v}_t))$$ lies on the lower-dimensional feasible manifold $$\mathcal{R}_{O_t}$$, it does not generally admit an ambient Lebesgue density. Formally, inference pushes the entity posterior forward through $$\psi_O$$, i.e., $$\mathbb{P}(\mathbf{r}_t \in \cdot \mid \mathbf{x}_t) = (\psi_O)_\# \mathbb{P}(\mathbf{v}_t \in \cdot \mid \mathbf{x}_t)$$, and the integral marginalises over feasible states in $$\mathcal{R}_{O_t}$$ (with sums for discrete variables).</d-footnote>

$$
\mathbb{P}(\mathbf{x}_{t+1} \mid \mathbf{x}_t, \mathbf{a}_t)
= \int_{\mathbf{r}_t, \mathbf{r}_{t+1}}
\underbrace{\mathbb{P}(\mathbf{x}_{t+1} \mid \mathbf{r}_{t+1})}_{\text{prediction}}
\underbrace{\mathbb{P}(\mathbf{r}_{t+1} \mid \mathbf{r}_t, \mathbf{a}_t)}_{\text{transition}}
\underbrace{\mathbb{P}(\mathbf{r}_t \mid \mathbf{x}_t)}_{\text{inference}}.
$$

This decomposition exposes the computational pipeline **infer $$\to$$ transition $$\to$$ predict**, while making its failure modes visible. If a logging policy acts on hidden information absent from $$\mathbf{x}_t$$, the third independence fails and posterior inference for logged data must condition on the action as $$\mathbb{P}(\mathbf{r}_t \mid \mathbf{x}_t, \mathbf{a}_t)$$. More importantly, even when all three independences hold, the factorisation still describes *observed transitions*, not yet controlled interventions.

Figure 2 summarises these interfaces as a **causal influence diagram (CID)** <d-cite key="everitt2021agent"></d-cite>, separating the solid computational/decision pipeline from dashed **omitted-factor confounding**. Suppose an unmodelled surface property $$\epsilon_x$$ (such as table roughness) creates both a visible texture cue in $$\mathbf{x}_t$$ and resistance when a block is pushed. If a logging policy uses that texture cue to push harder on rough surfaces, while the encoder discards texture from $$\mathbf{r}_t$$, then $$\epsilon_x$$ opens confounding paths $$\mathbf{a}_t \leftarrow \mathbf{x}_t \leftarrow \epsilon_x \to \mathbf{r}_{t+1}$$ and $$\mathbf{a}_t \leftarrow \mathbf{x}_t \leftarrow \epsilon_x \to \mathbf{u}_{t+1}$$. Conditioning on $$\mathbf{r}_t$$ alone fails to block either path.

<div class="l-body-outset">
  <img src="{{ '/assets/img/2027-04-30-what-makes-a-world-model-causal/cwm-cid.svg' | relative_url }}" alt="Causal influence diagram of CWM component interfaces showing observations, relational states, action node, random task score diamond, and dashed omitted-factor confounding paths." style="width:100%;max-width:860px;display:block;margin:auto;" />
</div>
<div class="caption"><strong>Figure 2.</strong> Causal influence diagram for the CWM component interfaces. Solid arrows represent inference (computational, not an environmental causal edge), policy information, transition, prediction, and task-score inputs into the random score \(\mathbf{u}_{t+1}\). Dashed red arrows show how an omitted factor \(\epsilon_x\) (e.g., surface roughness) can confound action responses and scores when a policy uses a visual cue discarded by \(\mathbf{r}_t\).</div>

## From representation to relational discovery

Before asking causal questions over $$\mathbf{r}_t$$, two upstream steps must hold together: recovering the right variables from observations, and discovering which dependencies among them are causal.

On the representation side, architectural symmetries (such as Slot Attention's permutation equivariance <d-cite key="locatello2020object"></d-cite>) do not by themselves establish physical identifiability. Population recovery results—whether via auxiliary-conditioned VAEs <d-cite key="khemakhem2020variational"></d-cite>, Gaussian-mixture priors with weakly injective decoders <d-cite key="kivva2022identifiability"></d-cite>, or additive decoders <d-cite key="lachapelle2024additive"></d-cite>—each recover representations only up to specific transformations (affine mixing or block-wise permutations and reparameterisations). Moreover, an invertible transformation of the whole state vector can mix blocks and distort conditional independences; even a scalar bijection like $$\widetilde Y = e^Y$$ preserves conditional independences while breaking additive-noise assumptions.

On the discovery side, placing both entity attributes and derived relations inside $$\mathbf{r}_t$$ exposes a subtle trap that standard causal discovery overlooks.

> **The deterministic-relation trap.** Take two block positions $$X_1, X_2$$, an action $$A$$, and next-step motion $$Y$$, with supplied displacement $$D = X_2 - X_1$$ and mechanism $$Y = \alpha D + \beta A + \varepsilon$$. Exposing $$D$$ captures translation invariance with one parameter instead of two. Yet inside the augmented variable set $$\{X_1, X_2, D, A, Y\}$$, we automatically have $$D \perp Y \mid (X_1, X_2)$$ because $$D$$ is deterministic given $$(X_1, X_2)$$! This violates standard *faithfulness*: naive conditional-independence discovery (such as vanilla PC <d-cite key="spirtes2000causation"></d-cite>) can delete the very relational edge $$D \to Y$$ it was meant to uncover.

Handling $$\mathcal{G}_r$$ faithfully therefore requires **determinism-aware discovery** <d-cite key="li2024deterministic"></d-cite> that separates supplied assembly constraints from environmental dependencies. And even in the faithful, causally sufficient case, observational conditional independences identify a directed acyclic graph (DAG) only up to **Markov equivalence** (same skeleton and unshielded colliders <d-cite key="verma1990equivalence"></d-cite>). Markov equivalence does not guarantee interventional agreement: the two Gaussian models $$\mathcal{M}_1: (X = N_X,\; Y = 0.8X + 0.6N_Y)$$ and $$\mathcal{M}_2: (Y = \widetilde N_Y,\; X = 0.8Y + 0.6\widetilde N_X)$$ induce the exact same observational distribution, yet yield $$\mathbb{E}_{\mathcal{M}_1}[Y \mid \operatorname{do}(X=x)] = 0.8x$$ versus $$\mathbb{E}_{\mathcal{M}_2}[Y \mid \operatorname{do}(X=x)] = 0$$.

## From prediction to causation

To move from predictive factorisations to causal claims, we equip the modelled variables with structural mechanisms $$Y_j = F_j(Y_{\mathrm{pa}(j)}, N_j)$$ driven by exogenous disturbances $$N \sim \mathbb{P}_N$$. An intervention $$\operatorname{do}(Y_j = y)$$ replaces the assignment for $$Y_j$$ while keeping the remaining mechanisms intact <d-cite key="pearl2009causality,scholkopf2021toward"></d-cite>.

Pearl's causal hierarchy organises queries into three rungs—**seeing (association)**, **doing (intervention)**, and **imagining (counterfactual reasoning)** <d-cite key="pearl2018bookofwhy,bareinboim2022on"></d-cite>. For world models built from unstructured pixels or sensors, we add **interpreting** as an explicit modelling layer (not a fourth Pearl rung) that maps observations to entity attributes and relational states. Figure 3 aligns these layers with the CWM components.

<div class="l-page">
  <img src="{{ '/assets/img/2027-04-30-what-makes-a-world-model-causal/causal-ladder.png' | relative_url }}" alt="Conceptual causal ladder of a Causal World Model connecting seeing, interpreting, doing, and imagining to inference, structured relational variables, causal graphs, transition, utility, and prediction components." style="width:100%;max-width:1100px;display:block;margin:auto;" />
</div>
<div class="caption"><strong>Figure 3.</strong> Conceptual causal ladder of a CWM. <em>Interpreting</em> is our added modelling layer between seeing and doing—<strong>not</strong> a fourth Pearl rung, despite the "RUNG 1-2" label left in the artwork—and it exposes entity attributes \(\mathbf{v}_t\), relational states \(\mathbf{r}_t\), and candidate causal graphs. Pearl's three causal rungs are seeing (association), doing (intervention), and imagining (counterfactual reasoning) <d-cite key="pearl2018bookofwhy,bareinboim2022on"></d-cite>. The inference, transition, prediction/emission, and utility components operate <em>across</em> rungs—prediction \(\mathbb{P}(\mathbf{x}_{t+1}\mid\mathbf{r}_{t+1})\) is not restricted to counterfactuals.</div>

At the observation level, the three causal rungs ask for strictly different distributions:

$$
\begin{aligned}
\text{Association (seeing):}\quad & \mathbb{P}(\mathbf{x}_{t+1} \mid h_t, \mathbf{a}_t = a), \\
\text{Intervention (doing):}\quad & \mathbb{P}(\mathbf{x}_{t+1} \mid h_t; \operatorname{do}(\mathbf{a}_t = a)), \\
\text{Episode counterfactual (imagining):}\quad & \mathbb{P}(\mathbf{x}_{t+1}^{a'} \mid e).
\end{aligned}
$$

Here $$h_t$$ is pre-action history, whereas $$e$$ is factual evidence from a specific realised episode (including its realised action and outcome), and $$\mathbf{x}_{t+1}^{a'}$$ is that *same* episode's response under an alternative action $$a'$$ with shared disturbances. Validity at one rung never automatically implies validity at a higher rung <d-cite key="bareinboim2022on"></d-cite>.

### From seeing to doing: identifying action effects

In a logged dataset generated by a behaviour policy $$b$$, the conditional transition $$\mathbb{P}_b(\mathbf{r}_{t+1} \mid \mathbf{r}_t, \mathbf{a}_t = a)$$ describes what followed when $$b$$ happened to choose $$a$$. The interventional response $$K_t^{\mathrm{do}}(\cdot \mid r, a) := \mathbb{P}(\mathbf{r}_{t+1} \in \cdot \mid \mathbf{r}_t = r; \operatorname{do}(\mathbf{a}_t = a))$$ describes what follows when we *force* $$a$$. Identifying $$K_t^{\mathrm{do}}$$ from logged transitions requires four explicit conditions <d-cite key="hernan2020whatif,pearl2009causality"></d-cite>:

1. **Mechanism invariance (modularity):** replacing the action policy leaves the physical transition mechanisms and disturbance distribution unchanged.
2. **Consistency:** when the observed action is $$\mathbf{a}_t = a$$, the observed next state equals the potential outcome $$\mathbf{r}_{t+1}^a$$.
3. **Exchangeability (no hidden action confounding):** $$\mathbf{r}_{t+1}^a \perp \mathbf{a}_t \mid \mathbf{r}_t$$—the retained state blocks all confounding paths (violated in Figure 2 if $$\epsilon_x$$ is omitted).
4. **Positivity (coverage):** the target query's state–action law $$\rho_t$$ is dominated by the logged occupancy law $$d_t^b$$ ($$\rho_t \ll d_t^b$$), so the model is not extrapolating to actions never tried in the relevant states.

Evaluating a multi-step target policy $$\pi$$ over horizon $$T$$ adds two further requirements: **temporal Markov sufficiency** (or an explicit history-dependent kernel $$Q_t^{\mathrm{do}}(\cdot \mid h_t, a)$$ when current state omits relevant past memory) and **sequential trajectory coverage** across the rollout steps.

### From doing to imagining: episode-conditioned counterfactuals

Even if a model learns every interventional kernel *perfectly*, it still does not generally identify what would have happened in a single realised episode under an alternative action.

> **Identical interventions, opposite counterfactuals.** Fix an initial state, randomise $$A \in \{0,1\}$$ independently, and let $$N \sim \mathrm{Bernoulli}(1/2)$$. Compare two structural models <d-cite key="oberst2019counterfactual"></d-cite>:
>
> $$\mathcal{M}_1:\; Y = N \qquad\text{versus}\qquad \mathcal{M}_2:\; Y = N \oplus A,$$
>
> where $$\oplus$$ is XOR. Both models induce the exact same logged joint law and identical interventional kernels $$\mathbb{P}(Y=1 \mid \operatorname{do}(A=a)) = 1/2$$ for every $$a$$. Now observe episode evidence $$e = \{A = 0, Y = 0\}$$, which pins down $$N = 0$$ in both models. Under the alternative action $$A = 1$$:
>
> $$\mathbb{P}_{\mathcal{M}_1}(Y^1 = 1 \mid e) = 0, \qquad \mathbb{P}_{\mathcal{M}_2}(Y^1 = 1 \mid e) = 1.$$
>

Evaluating an episode counterfactual requires **abduction** ($$\mathbb{P}_N(\cdot \mid e)$$), **intervention**, and **prediction** through a specified **cross-action coupling** of disturbances—information that interventional marginals alone do not determine. In discrete settings, a Gumbel-Max SCM supplies one explicit coupling assumption <d-cite key="oberst2019counterfactual"></d-cite>. In continuous latent dynamics, *Counterfactual World Models: JEPAs That Reason About "What If"* <d-cite key="balestriero2026counterfactual"></d-cite> reaches the same non-identifiability conclusion for factual action-conditioned predictors and shows that under additional physical restrictions—specifically sufficiently separate action and disturbance channels—a residual-based estimator becomes viable. In an additive regime, its intuitive form is

$$
\widehat z_{t+1}(a') = z_{t+1} + \mu(H_t, a') - \mu(H_t, a),
$$

where the observed factual outcome $$z_{t+1}$$ carries information about the realised disturbance and $$\mu$$ estimates how the predictable response shifts with action. Its short-time guarantees depend strictly on those structural and smoothness assumptions; contact events and action-dependent disturbances can invalidate the approximation.

The lesson is not that JEPAs or generative models are inherently causal or noncausal. It is that **causal capability is a property of a query, its semantics, the evidence, and the assumptions**—not an architectural label.

## Identifiability is relative to the question

Suppose two candidate models $$W_1, W_2 \in \mathfrak{W}$$ generate the exact same observable data distribution $$\mathbb{P}_{\mathfrak{D}}(W_1) = \mathbb{P}_{\mathfrak{D}}(W_2)$$ under an evidence regime $$\mathfrak{D}$$. Requiring **strong identifiability** ($$W_1 = W_2$$ up to exact labelled functions and laws) is often unnecessarily strict: swapping the internal slots for the red and blue blocks is harmless if every downstream module respects that swap.

Instead, let $$\mathcal{Q}$$ be the declared family of downstream queries expressed in a common semantic frame. Define **query-equivalence** by

$$
W_1 \sim_{\mathcal{Q}} W_2 \;\Longleftrightarrow\; q(W_1) = q(W_2) \quad \forall q \in \mathcal{Q}.
$$

Then **query-relative (weak) identifiability** asks for the weakest equivalence class preserving the answers we actually use:

$$
\mathbb{P}_{\mathfrak{D}}(W_1) = \mathbb{P}_{\mathfrak{D}}(W_2) \;\Longrightarrow\; W_1 \sim_{\mathcal{Q}} W_2.
$$

This viewpoint explains why different CWM components naturally live in different equivalence classes: representations up to affine or block-permutation maps <d-cite key="kivva2022identifiability,lachapelle2024additive"></d-cite>, causal graphs up to Markov equivalence <d-cite key="verma1990equivalence"></d-cite>, and decision states up to value equivalence <d-cite key="grimm2020value"></d-cite>. It also explains why **enlarging $$\mathcal{Q}$$**—from next-frame prediction to action effects, from one task reward to many, or from policy averages to episode counterfactuals—can suddenly make previously harmless ambiguities consequential <d-cite key="rubenstein2017causal,scholkopf2021toward"></d-cite>.

## Can world-model components be reused?

Even when every component is locally identifiable up to its own equivalence class, composing separately trained modules can silently fail if their coordinate conventions disagree. Two concrete tabletop failures illustrate why:

1. **Slot–action mismatch:** Suppose an entity encoder learns the two blocks up to a slot swap, $$T_V(p_R, p_B) = (p_B, p_R)$$, while its decoder and utility reader know slot 2 is red. A separately trained transition module expects red in slot 1, so action `push red` increments slot 1 instead of slot 2. Every module is valid in its own frame, yet their composition **reverses the action ranking** and pushes the wrong block.
2. **Relation-scale mismatch:** Suppose a contact relation outputs $$g(v) = \beta\,\mathbf{1}\{0 < p_B - p_R \le 1\}$$ with true contact probability $$\beta = 1/4$$, so pushing red twice reaches a joint goal with probability $$J_2 = \beta^2 = 1/16$$. If a learned relation module outputs a rescaled quantity $$m = 2g$$ (compensated during its own training by a receiver that divides by $$2$$), plugging $$m$$ into a new receiver expecting probability units turns $$\beta = 1/4$$ into $$1/2$$ and inflates the predicted two-step value to $$1/4$$. Notice that $$m = 1/2$$ still lies in $$[0,1]$$—**neither probability-range checks nor pixel reconstruction error will catch this bug**.

### Common alignment and adaptors

Safe reuse requires **compositional compatibility** under a shared set of bimeasurable bijections: $$T_V$$ on entity attributes, $$T_R$$ on feasible relational states, $$T_A$$ on entity-directed actions, and $$T_S(x, r) = (x, T_R(r))$$ on formal states (when observations remain in the same physical frame). Consistent composition requires all four interfaces to commute together:

$$
\begin{aligned}
\text{Assembly:}\quad & \widetilde\psi_O(T_V(v)) = T_R(\psi_O(v)), \\
\text{Transition:}\quad & \widetilde K_t^{\mathrm{do}}\!\left(\cdot \mid T_R(r), T_A(a)\right) = (T_R)_\# K_t^{\mathrm{do}}(\cdot \mid r, a), \\
\text{Policy:}\quad & \widetilde\pi_t\!\left(\cdot \mid T_R(r)\right) = (T_A)_\# \pi_t(\cdot \mid r), \\
\text{Utility:}\quad & \widetilde{\mathcal{U}}\!\left(T_A(a), T_S(s)\right) = \mathcal{U}(a, s),
\end{aligned}
$$

where $$(T)_\# \mathbb{P}$$ denotes the pushforward measure (for discrete spaces, the transition condition simplifies to pointwise equality $$\widetilde{\mathbb{P}}(T_R(r') \mid T_R(r), T_A(a)) = \mathbb{P}(r' \mid r, a)$$).<d-footnote>When utility depends on decoded observations, the conditional emission kernel must also align: $$\widetilde D_t(\cdot \mid T_R(r)) = D_t(\cdot \mid r)$$. For history-dependent policies, $$T_R$$ and $$T_A$$ apply componentwise across the history $$h_t$$.</d-footnote>

When two information-preserving components use different internal coordinates $$T_\ell y$$ and $$T_k y$$, a lightweight **adaptor** $$A_{\ell \to k} = T_k \circ T_\ell^{-1}$$—identified from paired object anchors, calibrated measurements, or synchronised actuator logs—can align them without forcing globally canonical coordinates. Under these alignment equations (plus matching initial laws), **finite-horizon trajectory laws and expected policy values are preserved; supremal values agree, and the sets of maximising policies correspond whenever maxima are attained** (conditional finite-horizon preservation).

Two strict limits remain:
- **Adaptors fix translations, not lost information.** Consider two bits $$(b_1, b_2)$$ with dynamics $$b_1' = a,\; b_2' = b_2$$. A representation $$z = b_1$$ is completely sufficient for the task score $$\mathbf{1}\{b_1' = 1\}$$, but for the new task $$\mathbf{1}\{b_1' = b_2\}$$ it achieves expected score $$1/2$$ instead of $$1$$. No adaptor applied to $$z$$ alone can restore the discarded bit $$b_2$$.
- **Kernel alignment does not preserve episode counterfactuals.** Preserving $$\mathbb{P}(Y^{a'} \mid e)$$ requires an additional noise alignment $$T_N$$ and **structural commutation** $$\widetilde F(T_R(r), T_A(a), T_N(n)) = T_R(F(r, a, n))$$ together with matching conditional noise posteriors. This is distinct from cross-action counterfactual ambiguity <d-cite key="rubenstein2017causal,oberst2019counterfactual,balestriero2026counterfactual"></d-cite>: one concerns coupling disturbances across actions, the other aligning interfaces across learned components.

### From population alignment to real rollouts

Even when component interfaces align in principle, finite-sample approximation errors do not stay local during planning. By a simulation-lemma argument <d-cite key="kearns2002near"></d-cite>, uniform one-step total-variation kernel error $$\epsilon_K$$ compounds across a horizon $$T$$ to bound policy-value error at $$O(T^2 \epsilon_K)$$—and low average error on the logged dataset does not guarantee low error on the states a planner actively seeks out. Likewise, a decoder trained on encoded real observations ($$q_{\mathrm{agg}}$$) can fail on imagined rollout latents ($$q_{\mathrm{roll}}$$) even without literal support holes <d-cite key="hoffman2016elbo"></d-cite>: for any bounded decoder error $$e_{\mathrm{dec}} \in [0, 1]$$,

$$
\mathbb{E}_{q_{\mathrm{roll}}}[e_{\mathrm{dec}}] \;\le\; \mathbb{E}_{q_{\mathrm{agg}}}[e_{\mathrm{dec}}] + \operatorname{TV}(q_{\mathrm{roll}}, q_{\mathrm{agg}}).
$$

Practical evaluation should therefore report interface alignment, rollout occupancy shift, and decision value separately, rather than relying on a single reconstruction or aggregate task score.

## What should we ask of a causal world model?

A practical specification can be short. Before calling a learned world model *causal*—or reusing one of its components in a new pipeline—ask five questions:

1. **State:** Which entities, attributes, relations, or latent distinctions does it retain, and what assembly constraints make a state feasible?
2. **Objective:** Which observation, representation, or decision signals trained it—and which distinctions did those signals leave unconstrained?
3. **Mechanisms:** How are supplied assembly constraints separated from environmental causal mechanisms, and what does an intervention actually modify?
4. **Evidence:** Are action effects backed by experiments or explicit identification assumptions (modularity, consistency, exchangeability, coverage)—and what structural coupling justifies any episode counterfactual?
5. **Identifiability and reuse:** Which query answers are invariant across observationally equivalent models, and do composed components share compatible alignments (or verified adaptors) under rollout support?

Not every useful world model must answer counterfactuals. A video predictor can be excellent without a structural causal model; a control model can be valuable without explicit objects. But **a causal world model should make its causal commitments testable**: declare the represented variables, mechanisms, supported queries, assumptions, and limits of identification.

That is the point of a component-level specification: not to rename every predictor, but to make clear **which questions about the world a learned model can legitimately answer**.

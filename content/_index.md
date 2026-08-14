---
title: ''
summary: ''
date: 2026-08-14
type: landing

sections:
  - block: resume-biography-3
    id: home
    content:
      username: me
      text: |-
        I am an astrophysics researcher at the **[Jeremiah Horrocks Institute](https://www.star.uclan.ac.uk)**, *[University of Lancashire](https://www.lancashire.ac.uk)*, and part of the [Galaxy Dynamics](https://www.star.uclan.ac.uk/~vpd/) research group led by Prof. Victor P. Debattista. My research combines galaxy simulations with observations to study the formation and evolution of barred galaxies and the Milky Way. In particular, I investigate the kinematics, chemistry, and ages of stellar populations in box/peanut (X-shaped) bulges, with recent work spanning bulge velocity ellipsoids, RR Lyrae and Mira variable stars, and the structure of the Milky Way's star-forming disc.

        My PhD was funded by the [Moses Holden](/outreach/mholden/) Studentship, dedicated to the Lancashire astronomer and educator. I am currently a Junior Associate of the [LSST:UK Consortium](https://www.lsst.ac.uk) as part of the [Galaxies; Stars, Milky Way and Local Volume Science Collaboration](https://milkyway.science.lsst.org) and a member of the [N-Body Shop](https://nbody.shop/index.html). Part of my current [research](/research/), **Gough-Kelly et al. ([2022](/publications/pmbs/))**, bridges these two memberships by making predictions for kinematic differences between populations within the Milky Way bulge.

      button:
        text: Download CV
        url: media/SGK-CV.pdf
      headings:
        about: Welcome...
        education: Education
        interests: Interests
    design:
      background:
        gradient_mesh:
          enable: true
      name:
        size: md
      avatar:
        size: medium
        shape: circle
  - block: markdown
    id: research
    content:
      title: Research
      subtitle: ''
      text: |-
        Galaxy dynamics helps us understand how galaxies form and evolve over time. My research focuses on the evolution of the central structures of disc galaxies, such as bars, nuclear discs, and bulges in galaxies similar to the Milky Way.

        We are particularly interested in the slow internal processes that dominate large-scale changes over the billions of years following the initial turbulent formation period.

        [Read more about my research](/research/).
    design:
      columns: '1'
  - block: collection
    id: papers
    content:
      title: Publications
      filters:
        folders:
          - publications
        featured_only: true
    design:
      view: article-grid
      columns: 2
  - block: collection
    content:
      title: Recent Publications
      text: ''
      filters:
        folders:
          - publications
        exclude_featured: false
    design:
      view: citation
---

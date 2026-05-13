---
title: ''
summary: ''
date: 2022-10-24
type: landing

sections:
  - block: resume-biography-3
    id: home
    content:
      username: me
      text: |-
        I am a PhD research student at the **[Jeremiah Horrocks Institute](https://www.star.uclan.ac.uk)**, *[University of Central Lancashire](https://www.uclan.ac.uk)* as part of the [Galaxy Dynamics](https://www.star.uclan.ac.uk/~vpd/) research group led by Prof. Victor P. Debattista. My primary research is studying the formation and evolution of box/peanut bulges in barred galaxies by comparing isolated and cosmological simulations to observations of external galaxies and the Milky Way.

        My position is funded by the [Moses Holden](/outreach/mholden/) Studentship, dedicated to the Lancashire astronomer and educator. I am currently a Junior Associate of the [LSST:UK Consortium](https://www.lsst.ac.uk) as part of the [Galaxies; Stars, Milky Way and Local Volume Science Collaboration](https://milkyway.science.lsst.org) and a member of the [N-Body Shop](https://nbody.shop/index.html). Part of my current [research](/research/), **Gough-Kelly et al. ([2022](/publications/pmbs/))**, bridges these two memberships by making predictions for kinematic differences between populations within the Milky Way bulge.

        I am also currently **Vice Chair** of the [Royal Astronomical Society](https://ras.ac.uk/) Early Career Network Steering Committee. Find out more about the network [here](https://ras.ac.uk/education-and-careers/early-career-network-meet-team).
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
  - block: markdown
    id: contact
    content:
      title: Contact
      subtitle: Feel free to get in contact with any questions or queries.
      text: |-
        <form class="sgk-contact-form" action="mailto:sgoughkelly@gmail.com" method="post" enctype="text/plain">
          <div class="sgk-form-grid">
            <label>
              <span>Name</span>
              <input type="text" name="name" autocomplete="name" required>
            </label>
            <label>
              <span>Email</span>
              <input type="email" name="email" autocomplete="email" required>
            </label>
          </div>
          <label>
            <span>Message</span>
            <textarea name="message" rows="6" required></textarea>
          </label>
          <button type="submit">Send message</button>
        </form>
    design:
      columns: '1'
---

# `autobot` in a container

**Last modified:** Jan 2020

Everything here uses `docker-compose`. We have 3 containers that we work from, but two of them are mutually exclusive.

- `autobot-development`
- `autobot-production`
- `autobot-hugo`

Both containers make use of an entrypoint script, as you can see in this directory. Entrypoint handles most of the semi-complex logic that hasn't been totally integrated into the container. There are TODOs listed throughout the `Dockerfile` and `entrypoint`, but these are pretty low-priority migrations at this point.

## Directories

The directories we're concerned with are listed below. There are further explanations about what these volumes (within the container) house below.

```bash
/
├── autobot
├── ucfai
└── ucfai.org
```

### `/autobot/` &ndash; only used in `autobot-development`

This locally mounts the `bot` so that development changes are reflected within the container and be run.

### `/ucfai/` &ndash; used in both `autobot-development` and `autobot-production`

**In `development`:** the local directory (`groups/`) is mounted so that we can see the changes being made to each group. `groups/` is deliberately untracked to avoid having to deal with `git submodule` voodoo, especially since `autobot` is intended to operate over the latest changes but doesn't depend on a specific version of a group.

**In `production`:** the local directory isn't mounted, but the `entrypoint` script still clones the groups to operate over them.

### `/ucfai.org/` &ndash; used in `autobot-development` and `autobot-hugo`

Since `autobot` makes changes that also update the website, we maintain a local Hugo server so that we can see changes as `autobot` produces them.

- **In `autobot-development`:** this volume is mounted at `/ucfai.org/`.
- **In `autobot-hugo`:** this volume is mounted at `/src/`.

## Usage

This makes heavy use of `docker-compose`.

### Initial setup (first time use in the `autobot-development` container)

1. `docker-compose up`

   > You'll see quite a bit of streaming output as the `autobot-development` container executes a first-time setup that clones the needed repositories.

2. When you see the following output, you're good to quit the `docker-compose` cluster. (`autobot-hugo` may make some complaints, we'll resolve those in the next step.)

   > ```bash
   > autobot-development    | Cloning groups...
   > autobot-development    | /ucfai/core -> cloning
   > autobot-development    | /ucfai/intelligence -> cloning
   > autobot-development    | /ucfai/data-science -> cloning
   > autobot-development    | /ucfai/supplementary -> cloning
   > autobot-development    | /ucfai/gbm -> cloning
   > autobot-development    | /ucfai.org -> cloning
   > autobot-development    |   - updated submodules
   > ```

3. `docker-compose down`
   > Execute this to make sure you destroy the containers and network, so that the next time you start things up it will work as expected.

4. Check that you're on the expected branches within each of the repositories in `groups/` and in the `ucfai.org/` repository (found in this folder).
5. Setup complete!

### Actually spinning up the containers

Due to limited knowledge of conditionally spinning up containers in `docker-compose` (and a lacking need for this at the moment), `autobot-production` is commented out to avoid building and running, since we don't need this for local development.

Now that all the `groups/` and `ucfai.org/` are properly initialized, you should start the `docker-compose` cluster by running:

```bash
docker-compose up -d
```

This should output something similar to:

> ```bash
> Starting autobot-hugo        ... done
> Starting autobot-development ... done
> ```

Follow standard `docker-compose` usage to view things like the logs and such. To interact with `autobot`, and more broadly the container, use the following:

- ```bash
  docker-compose run autobot-development
  ```

  To spawn the "endless waiter" (this will keep the container running so that we can actually use `docker-compose run autobot-development <cmd>` without needing to constantly restart the container)

- ```bash
  docker-compose run autobot-development bash
  ```

  To enter the container's shell (**CAREFUL**: change made in here will _not_ persist when restarting the container)

- ```bash
  docker-compose run autobot-development <cmd>
  ```

  Will drop you into interacting with `autobot` – treat this as if you're running `autobot <cmd>`.

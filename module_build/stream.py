

class ModuleStream:

    def __init__(self, mmd, version):

        self.mmd = mmd

        self.name = mmd.get_module_name()
        if not self.name:
            # TODO name is taked from the repo name when building from a SCM. When building localy
            # we need to find out if we will provide some automatic substitution or error out
            raise Exception(("The module stream metadata file does not provide a name for the "
                             "module!"))
        self.stream = mmd.get_stream_name()
        if not self.stream:
            # TODO stream is taked from the branch name when building from a SCM. When building
            # localy we need to find out if we will provide some automatic substitution or error out
            raise Exception(("The module stream metadata file does not provide a name for the "
                             "stream!"))

        self.version = version
        self.description = mmd.get_description()

        self.contexts = self.process_build_configurations(mmd)

        self.components = self.process_components(mmd)

    def process_build_configurations(self, mmd):
        index = mmd.convert_to_index()
        streams = index.search_streams()

        contexts = []
        for s in streams:
            # we need to get the platform from the buildconfig which is defined in the packager
            # metadata document.
            context_name = s.get_context()
            bc = mmd.get_build_config(context_name)
            platform = bc.get_platform()

            msc = ModuleStreamContext(s, self.version, platform)
            contexts.append(msc)
        return contexts

    def process_components(self, mmd):

        comp_names = mmd.get_rpm_component_names()

        components = []

        for name in comp_names:
            comp_md = mmd.get_rpm_component(name)

            component = {}
            component["name"] = comp_md.get_name()
            component["arches"] = comp_md.get_arches()
            # TODO: check if buildorder and buildafter are mutually exclusive
            component["buildafter"] = comp_md.get_buildafter()
            component["buildonly"] = comp_md.get_buildonly()
            component["buildorder"] = comp_md.get_buildorder()
            component["buildroot"] = comp_md.get_buildroot()
            component["multilib_arches"] = comp_md.get_multilib_arches()
            component["rationale"] = comp_md.get_rationale()
            component["ref"] = comp_md.get_ref()
            component["repository"] = comp_md.get_repository()
            component["srpm_buildroot"] = comp_md.get_srpm_buildroot()

            components.append(component)

        return components


class ModuleStreamContext:

    def __init__(self, mmd, version, platform):
        self.mmd = mmd
        mmd.set_version(version)
        mmd.set_static_context()
        self.static_context = mmd.is_static_context()
        self.module_name = mmd.get_module_name()
        self.version = version
        self.platform = platform
        self.stream = mmd.get_stream_name()
        self.context_name = mmd.get_context()
        self.build_opts = mmd.get_buildopts()
        self.rpm_macros = self.build_opts.get_rpm_macros().split("\n")
        self.rpm_whitelist = self.build_opts.get_rpm_whitelist()
        self.dependencies = self._get_dependencies(mmd)
        self.demodularized_rpms = mmd.get_demodularized_rpms()

    def get_NSVCA(self):
        return self.mmd.get_NSVCA()

    def set_arch(self, arch):
        """A helper function for setting the arch of the build.

        :param arch: operating system architecture i. e. x86_64, s390 etc.
        :type arch: str
        """
        self.mmd.set_arch(arch)
        self.arch = arch

    def _get_dependencies(self, mmd):
        dependencies = mmd.get_dependencies()[0]
        processed_deps = {
            "buildtime": [],
            "runtime": [],
        }

        buidtime_dep_names = dependencies.get_buildtime_modules()
        for name in buidtime_dep_names:
            # NOTE: platform is not a real build or runtime dependency.
            if name != "platform":
                stream = dependencies.get_buildtime_streams(name)
                processed_deps["buildtime"].append("{name}:{stream}".format(name=name,
                                                                            stream=stream))
        runtime_dep_names = dependencies.get_runtime_modules()

        for name in runtime_dep_names:
            # NOTE: platform is not a real build or runtime dependency.
            if name != "platform":
                stream = dependencies.get_runtime_streams(name)
                processed_deps["runtime"].append("{name}:{stream}".format(name=name, stream=stream))

        return processed_deps

    def get_modularity_label(self):
        return "{name}:{stream}:{version}:{context}".format(name=self.module_name,
                                                            stream=self.stream, 
                                                            version=self.version, 
                                                            context=self.context_name)

    def get_rpm_suffix(self):
        return ".module_{platform}+{context}".format(platform=self.platform,
                                                     context=self.context_name)

from customizations.dashboards.project.instances.workflows \
    import create_instance as customized_create_instance
from openstack_dashboard.dashboards.project.instances import views
from openstack_dashboard.dashboards.project.instances.workflows \
    import create_instance


class LaunchInstanceViewCustomizer:

    def execute(self):
        """replace SetAccessControls with CustomSetAccessControls
           to make a keypair selection required.
        """
        views.LaunchInstanceView.workflow_class.default_steps = \
            self.get_default_steps()

    def get_default_steps(self):
        return (create_instance.SelectProjectUser,
                create_instance.SetInstanceDetails,
                # customized access control tab
                customized_create_instance.CustomSetAccessControls,
                create_instance.SetNetwork,
                create_instance.PostCreationStep,
                create_instance.SetAdvanced)
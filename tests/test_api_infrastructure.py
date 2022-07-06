import json
import pathlib
import tempfile
import unittest

from aws_cdk import core as cdk

from s3.infrastructure import BucketHelmRepo


class BucketHelmRepoTestCase(unittest.TestCase):

    def test_create_bucket_helm_repo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            app = cdk.App(outdir=temp_dir)
            stack = cdk.Stack(app, "Stack")


            bucketHelmRepo = BucketHelmRepo(stack, "bucketHelmRepo-Id", name="bucket-helm-repo-name")
            cloud_assembly = app.synth()
            template = cloud_assembly.get_stack_by_name(stack.stack_name).template
            # print(template["Resources"])
            bucketId = next(iter(template["Resources"]))
        self.assertEqual(
            template["Resources"][bucketId]["Properties"]["BucketName"],
            "bucket-helm-repo-name",
        )    
        self.assertEqual(
            template["Resources"][bucketId]["UpdateReplacePolicy"],
            "Delete",
        )
        self.assertEqual(
            template["Resources"][bucketId]["DeletionPolicy"],
            "Delete",
        )

if __name__ == "__main__":
    unittest.main()

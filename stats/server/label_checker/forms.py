from django import forms

#TODO use file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
class InputForm(forms.Form):
    image_1 = forms.CharField(label='Image1', max_length=254, help_text='Enter image 1', required=False)
    image_2 = forms.CharField(label='Image2', max_length=254, help_text='Enter image 2', required=False)
    label_1 = forms.FileField(label='Label1', help_text='Enter label of image 1', required=False)
    label_2 = forms.FileField(label='Label2', help_text='Enter label of image 2', required=False)
    predicted_label = forms.FileField(label='pred_label1', help_text='Enter predicted label of image 1 for bounding box QA',
                                       required=False)
    #predicted_label2 = forms.FileField(label='pred_label2', help_text='Enter predicted label of image 2 for bounding box QA',
    #                                   required=False)
    segmantic_seg = forms.BooleanField(label='EnableSemanticSegmentation', help_text='Select semantic segmentation', required=False)
    bounding_box = forms.BooleanField(label='EnableBoundingBox', help_text='Select bounding box', required=False)

    # related to google cloud
    image_storage = forms.FileField(label='image_storage', help_text='Enter storage on cloud where images are saved', required=False)
    image_folder = forms.FileField(label='image_folder', help_text='Enter folder on cloud where images are saved', required=False)
    private_key_cloud = forms.FileField(label='private_key_cloud', help_text='Enter private key of cloud', required=False)

    #for batch processing
    batch_processing = forms.BooleanField(label='EnableBatchProcessing', help_text='Select batch processing', required=False)
    count_of_images = forms.IntegerField(label='CountOfImages', help_text='Number of images for batch processing', required=False)

    instance_mask_path = forms.CharField(label='InstanceMaskPath', max_length=1000, help_text='Enter instance mask path for batch processing', required=False)
    #image_path = forms.CharField(label='ImagePath', max_length=1000, help_text='Enter image path', required=False)

    def clean(self):
        #cleaned_data = super(InputForm, self).clean()
        image_1 = self.cleaned_data.get('image_1')
        image_2 = self.cleaned_data.get('image_2')
        label_1 = self.cleaned_data.get('label_1')
        label_2 = self.cleaned_data.get('label_2')
        if not image_1 and not image_2 and not label_1 and not label_2:
            raise forms.ValidationError('You have to write something!')
        return self.cleaned_data
from rest_framework import serializers


class StudentWithCustomSerializerSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()

    def create(self, validated_data):
        from test_basics.models import StudentWithCustomSerializer #using local import to prevernt
        #circular import
        return StudentWithCustomSerializer.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance